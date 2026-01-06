/**
 * Unit Tests for DataCache
 * Tests multi-level caching functionality
 */

// Define mock factory BEFORE imports to ensure it works even if hoisting is disabled by config
jest.mock('fs-extra', () => {
  return {
    stat: jest.fn(),
    readFile: jest.fn(),
    promises: {
      stat: jest.fn(),
      readFile: jest.fn(),
    }
  };
});

const DataCache = require('../../src/analytics/data/DataCache');
const fs = require('fs-extra');

describe('DataCache', () => {
  let dataCache;
  const mockStats = {
    mtime: { getTime: () => 1000 },
    size: 1024
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock implementation
    fs.stat.mockResolvedValue(mockStats);
    fs.readFile.mockResolvedValue('{"test": "data"}');
    
    // Also mock promises interface if used
    fs.promises.stat.mockResolvedValue(mockStats);
    fs.promises.readFile.mockResolvedValue('{"test": "data"}');
    
    dataCache = new DataCache();
  });

  afterEach(() => {
    if (dataCache) {
      dataCache.cleanup();
    }
  });

  describe('constructor', () => {
    it('should initialize with empty caches and metrics', () => {
      expect(dataCache.caches.fileContent).toBeInstanceOf(Map);
      expect(dataCache.caches.parsedConversations).toBeInstanceOf(Map);
      
      expect(dataCache.metrics.hits).toBe(0);
      expect(dataCache.metrics.misses).toBe(0);
    });

    it('should configure correctly', () => {
      dataCache.configure({
        fileContentTTL: 10000,
        maxCacheSize: 100
      });
      
      expect(dataCache.config.fileContentTTL).toBe(10000);
      expect(dataCache.config.maxCacheSize).toBe(100);
    });
  });

  describe('getFileContent', () => {
    const mockFilePath = '/test/file.jsonl';
    const mockContent = '{"test": "data"}';

    it('should read file when not cached', async () => {
      const content = await dataCache.getFileContent(mockFilePath);
      
      expect(content).toBe(mockContent);
      expect(fs.stat).toHaveBeenCalledWith(mockFilePath);
      expect(fs.readFile).toHaveBeenCalledWith(mockFilePath, 'utf8');
      expect(dataCache.metrics.misses).toBe(1);
      expect(dataCache.metrics.hits).toBe(0);
    });

    it('should return cached content when file unchanged', async () => {
      // First call - cache miss
      await dataCache.getFileContent(mockFilePath);
      
      // Second call - cache hit
      const content = await dataCache.getFileContent(mockFilePath);
      
      expect(content).toBe(mockContent);
      expect(fs.readFile).toHaveBeenCalledTimes(1);
      expect(dataCache.metrics.hits).toBe(1);
    });

    it('should re-read file when modified', async () => {
      // First call
      await dataCache.getFileContent(mockFilePath);
      
      // Update mock for second call
      const newerStats = { mtime: { getTime: () => 2000 }, size: 1024 };
      fs.stat.mockResolvedValueOnce(newerStats);
      fs.readFile.mockResolvedValueOnce('{"updated": "data"}');
      
      // Second call
      const content = await dataCache.getFileContent(mockFilePath);
      
      expect(content).toBe('{"updated": "data"}');
      expect(dataCache.metrics.misses).toBe(2);
    });

    it('should handle file read errors', async () => {
      fs.stat.mockRejectedValueOnce(new Error('File not found'));
      
      await expect(dataCache.getFileContent(mockFilePath)).rejects.toThrow('File not found');
    });
  });

  describe('getParsedConversation', () => {
    const mockFilePath = '/test/conversation.jsonl';
    const mockContent = '{"type": "user", "message": {"role": "user", "content": "hello"}}\n{"type": "assistant", "message": {"role": "assistant", "content": "hi"}}';

    beforeEach(() => {
      fs.readFile.mockResolvedValue(mockContent);
      fs.promises.readFile.mockResolvedValue(mockContent);
    });

    it('should parse conversation content correctly', async () => {
      const parsed = await dataCache.getParsedConversation(mockFilePath);
      
      expect(parsed).toHaveLength(2);
      expect(parsed[0].content).toBe('hello');
    });

    it('should cache parsed results', async () => {
      // First call
      await dataCache.getParsedConversation(mockFilePath);
      
      // Second call
      await dataCache.getParsedConversation(mockFilePath);
      
      expect(fs.readFile).toHaveBeenCalledTimes(1);
    });
  });

  describe('getCachedTokenUsage', () => {
    const mockFilePath = '/test/file.jsonl';
    const mockComputeFunction = jest.fn().mockResolvedValue({
      total: 1500
    });

    it('should compute and cache token usage', async () => {
      const result = await dataCache.getCachedTokenUsage(mockFilePath, mockComputeFunction);
      
      expect(result).toEqual({ total: 1500 });
      expect(mockComputeFunction).toHaveBeenCalledTimes(1);
    });

    it('should return cached result on subsequent calls', async () => {
      await dataCache.getCachedTokenUsage(mockFilePath, mockComputeFunction);
      const result = await dataCache.getCachedTokenUsage(mockFilePath, mockComputeFunction);
      
      expect(result).toEqual({ total: 1500 });
      expect(mockComputeFunction).toHaveBeenCalledTimes(1);
    });
  });

  describe('invalidateFile', () => {
    const mockFilePath = '/test/file.jsonl';

    it('should remove all cache entries for a file', () => {
      dataCache.caches.fileContent.set(mockFilePath, { content: 'test', timestamp: Date.now() });
      dataCache.invalidateFile(mockFilePath);
      expect(dataCache.caches.fileContent.has(mockFilePath)).toBe(false);
    });
  });

  describe('evictOldEntries', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should remove expired cache entries', () => {
      const now = Date.now();
      jest.setSystemTime(now);
      
      dataCache.caches.fileContent.set('/expired', {
        content: 'old',
        timestamp: now - 100000 
      });
      dataCache.caches.fileContent.set('/fresh', {
        content: 'new',
        timestamp: now
      });
      
      dataCache.evictOldEntries();
      
      expect(dataCache.caches.fileContent.has('/expired')).toBe(false);
      expect(dataCache.caches.fileContent.has('/fresh')).toBe(true);
    });
  });

  describe('getStats', () => {
    it('should return cache statistics', async () => {
      const stats = dataCache.getStats();
      expect(stats).toHaveProperty('hitRate');
      expect(stats).toHaveProperty('cacheSize');
    });
  });

  describe('cleanup', () => {
    it('should clear all caches', () => {
      dataCache.caches.fileContent.set('test', { data: 'test' });
      dataCache.cleanup();
      expect(dataCache.caches.fileContent.size).toBe(0);
    });
  });
});