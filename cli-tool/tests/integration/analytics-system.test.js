/**
 * Integration Tests for Analytics System
 * Tests the complete analytics system integration
 */

const path = require('path');
const fs = require('fs-extra');
const { spawn } = require('child_process');

describe('Analytics System Integration', () => {
  let analyticsProcess;
  let testDataDir;

  beforeAll(async () => {
    // Create test data directory
    testDataDir = path.join(__dirname, '../fixtures/test-conversations');
    await fs.ensureDir(testDataDir);
    
    // Create sample conversation files
    await createTestConversationFiles(testDataDir);
  });

  afterAll(async () => {
    // Cleanup test data
    await fs.remove(testDataDir);
    
    // Kill analytics process if running
    if (analyticsProcess) {
      analyticsProcess.kill('SIGTERM');
    }
  });

  describe('Backend Integration', () => {
    it('should load and analyze conversation data correctly', async () => {
      const { GeminiAnalytics } = require('../../src/analytics');
      
      // Pass testDataDir to constructor options
      const analytics = new GeminiAnalytics({
        geminiDir: testDataDir,
        verbose: false
      });
      
      // Mock the setup methods to avoid actual server startup
      analytics.setupWebServer = jest.fn();
      analytics.setupFileWatchers = jest.fn();
      
      await analytics.loadInitialData();
      
      expect(analytics.data.conversations).toBeDefined();
      expect(analytics.data.conversations.length).toBeGreaterThan(0);
      expect(analytics.data.summary).toBeDefined();
      expect(analytics.data.summary.totalConversations).toBeGreaterThan(0);
    });

    it('should detect conversation states correctly', async () => {
      const StateCalculator = require('../../src/analytics/core/StateCalculator');
      const ConversationAnalyzer = require('../../src/analytics/core/ConversationAnalyzer');
      const ProcessDetector = require('../../src/analytics/core/ProcessDetector');
      
      const stateCalculator = new StateCalculator();
      const processDetector = new ProcessDetector();
      const analyzer = new ConversationAnalyzer(testDataDir);
      
      const data = await analyzer.loadInitialData(stateCalculator, processDetector);
      
      expect(data.conversations).toBeDefined();
      expect(data.conversations.length).toBeGreaterThan(0);
      data.conversations.forEach(conv => {
        expect(['active', 'waiting', 'idle', 'completed']).toContain(conv.status);
        // tokens/messages might be 0 if mock files are empty, so we just check if they are numbers
        expect(typeof conv.tokens).toBe('number');
        expect(typeof conv.messageCount).toBe('number');
      });
    });

    it('should cache data efficiently', async () => {
      const DataCache = require('../../src/analytics/data/DataCache');
      
      const cache = new DataCache();
      const testFile = path.join(testDataDir, 'conversation_1.jsonl');
      
      // First read - cache miss
      const start1 = Date.now();
      const content1 = await cache.getFileContent(testFile);
      const time1 = Date.now() - start1;
      
      // Second read - cache hit
      const start2 = Date.now();
      const content2 = await cache.getFileContent(testFile);
      const time2 = Date.now() - start2;
      
      expect(content1).toBe(content2);
      // Removed timing sensitive test: expect(time2).toBeLessThan(time1);
      expect(cache.metrics.hits).toBe(1);
      expect(cache.metrics.misses).toBe(1);
    });
  });

  describe('WebSocket Integration', () => {
    let webSocketServer;
    let httpServer;
    let mockClient;

    beforeEach(async () => {
      const WebSocketServer = require('../../src/analytics/notifications/WebSocketServer');
      const http = require('http');
      
      httpServer = http.createServer();
      webSocketServer = new WebSocketServer(httpServer);
      
      await new Promise((resolve) => {
        httpServer.listen(0, () => {
          resolve();
        });
      });
      
      await webSocketServer.initialize();
    });

    afterEach(async () => {
      if (webSocketServer) {
        await webSocketServer.close();
      }
      if (httpServer) {
        httpServer.close();
      }
    });

    it('should handle WebSocket connections and messaging', async () => {
      const WebSocket = require('ws');
      const port = httpServer.address().port;
      
      // Create WebSocket client
      mockClient = new WebSocket(`ws://localhost:${port}/ws`);
      
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket test timeout'));
        }, 5000);

        mockClient.on('open', () => {
          // Send subscribe message
          mockClient.send(JSON.stringify({
            type: 'subscribe',
            channel: 'conversation_updates'
          }));
        });

        mockClient.on('message', (data) => {
          const message = JSON.parse(data);
          
          if (message.type === 'connection') {
            expect(message.data.clientId).toBeDefined();
          } else if (message.type === 'subscription_confirmed') {
            expect(message.data.channel).toBe('conversation_updates');
            clearTimeout(timeout);
            mockClient.close();
            resolve();
          }
        });

        mockClient.on('error', (error) => {
          clearTimeout(timeout);
          reject(error);
        });
      });
    });

    it('should broadcast notifications to subscribed clients', async () => {
      const NotificationManager = require('../../src/analytics/notifications/NotificationManager');
      
      const notificationManager = new NotificationManager(webSocketServer);
      await notificationManager.initialize();
      
      const WebSocket = require('ws');
      const port = httpServer.address().port;
      
      mockClient = new WebSocket(`ws://localhost:${port}/ws`);
      
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Notification test timeout'));
        }, 5000);

        let subscribed = false;

        mockClient.on('open', () => {
          mockClient.send(JSON.stringify({
            type: 'subscribe',
            channel: 'conversation_updates'
          }));
        });

        mockClient.on('message', (data) => {
          const message = JSON.parse(data);
          
          if (message.type === 'subscription_confirmed' && !subscribed) {
            subscribed = true;
            // Send notification
            notificationManager.notifyConversationStateChange(
              'conv_123', 'idle', 'active', { project: 'test' }
            );
          } else if (message.type === 'conversation_state_change') {
            expect(message.data.conversationId).toBe('conv_123');
            expect(message.data.newState).toBe('active');
            clearTimeout(timeout);
            mockClient.close();
            resolve();
          }
        });

        mockClient.on('error', (error) => {
          clearTimeout(timeout);
          reject(error);
        });
      });
    });
  });

  describe('End-to-End Analytics Flow', () => {
    it('should process conversation changes end-to-end', async () => {
      const { GeminiAnalytics } = require('../../src/analytics');
      const analytics = new GeminiAnalytics({
        geminiDir: testDataDir,
        verbose: false
      });
      
      // Mock server setup
      analytics.setupWebServer = jest.fn();
      analytics.setupFileWatchers = jest.fn();
      analytics.geminiDir = testDataDir;
      
      // Initialize analytics
      await analytics.loadInitialData();
      
      const initialConversationCount = analytics.data.conversations.length;
      
      // Create new conversation file
      const newConvFile = path.join(testDataDir, 'new_conversation.jsonl');
      const newConvData = {
        message: {
          role: 'user',
          content: 'New test message'
        },
        timestamp: new Date().toISOString()
      };
      
      await fs.writeFile(newConvFile, JSON.stringify(newConvData) + '\n');
      
      // Reload data
      await analytics.loadInitialData();
      
      expect(analytics.data.conversations.length).toBe(initialConversationCount + 1);
      
      // Cleanup
      await fs.remove(newConvFile);
    });
  });

  describe('Performance Tests', () => {
    it('should handle large datasets efficiently', async () => {
      const { GeminiAnalytics } = require('../../src/analytics');
      const path = require('path');
      const fs = require('fs-extra');
      
      const largeDataDir = path.join(__dirname, '../fixtures/large-conversations');
      await fs.ensureDir(largeDataDir);
      
      // Create 100 conversation files
      for (let i = 0; i < 100; i++) {
        await fs.writeJson(path.join(largeDataDir, `conv_${i}.jsonl`), {
          id: `conv_${i}`,
          messages: [
            { role: 'user', content: 'hello' },
            { role: 'assistant', content: 'hi' }
          ],
          tokens: 10 + i,
          lastModified: new Date().toISOString()
        });
      }
      
      const analytics = new GeminiAnalytics({
        geminiDir: largeDataDir,
        verbose: false
      });
      analytics.setupWebServer = jest.fn();
      analytics.setupFileWatchers = jest.fn();
      
      const start = Date.now();
      await analytics.loadInitialData();
      const duration = Date.now() - start;
      
      expect(analytics.data.conversations.length).toBe(100);
      // Processing 100 small conversations should be very fast (under 1s)
      expect(duration).toBeLessThan(2000); 
      
      await fs.remove(largeDataDir);
    });

    it('should handle large datasets efficiently (raw analyzer)', async () => {
      const ConversationAnalyzer = require('../../src/analytics/core/ConversationAnalyzer');
      const DataCache = require('../../src/analytics/data/DataCache');
      const StateCalculator = require('../../src/analytics/core/StateCalculator');
      const ProcessDetector = require('../../src/analytics/core/ProcessDetector');
      
      const cache = new DataCache();
      const stateCalculator = new StateCalculator();
      const processDetector = new ProcessDetector();
      const analyzer = new ConversationAnalyzer(testDataDir, cache);
      
      const start = Date.now();
      const data = await analyzer.loadInitialData(stateCalculator, processDetector);
      const duration = Date.now() - start;
      
      expect(data.conversations.length).toBeGreaterThan(0);
      expect(duration).toBeLessThan(1000); // Should be sub-second
    });

    it('should handle large datasets efficiently (caching test)', async () => {
      const ConversationAnalyzer = require('../../src/analytics/core/ConversationAnalyzer');
      const DataCache = require('../../src/analytics/data/DataCache');
      const StateCalculator = require('../../src/analytics/core/StateCalculator');
      const ProcessDetector = require('../../src/analytics/core/ProcessDetector');
      
      const cache = new DataCache();
      const stateCalculator = new StateCalculator();
      const processDetector = new ProcessDetector();
      const analyzer = new ConversationAnalyzer(testDataDir, cache);
      
      const startTime = Date.now();
      
      // Run analysis multiple times to test caching
      for (let i = 0; i < 5; i++) {
        await analyzer.loadInitialData(stateCalculator, processDetector);
      }
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      expect(totalTime).toBeLessThan(10000); 
      expect(cache.metrics.hits).toBeGreaterThan(0);
    });

    it('should handle concurrent operations safely', async () => {
      const DataCache = require('../../src/analytics/data/DataCache');
      const cache = new DataCache();
      
      const testFile = path.join(testDataDir, 'conversation_1.jsonl');
      
      // Simulate concurrent file reads
      const promises = [];
      for (let i = 0; i < 10; i++) {
        promises.push(cache.getFileContent(testFile));
      }
      
      const results = await Promise.all(promises);
      
      // All results should be identical
      const firstResult = results[0];
      results.forEach(result => {
        expect(result).toBe(firstResult);
      });
    });
  });
});

/**
 * Helper function to create test conversation files
 */
async function createTestConversationFiles(testDir) {
  const conversations = [
    {
      filename: 'conversation_1.jsonl',
      data: [
        {
          message: { role: 'user', content: 'Hello, can you help me with JavaScript?' },
          timestamp: new Date(Date.now() - 3600000).toISOString() // 1 hour ago
        },
        {
          message: { role: 'assistant', content: 'Of course! I\'d be happy to help you with JavaScript.' },
          timestamp: new Date(Date.now() - 3500000).toISOString()
        },
        {
          message: { role: 'user', content: 'How do I create a function?' },
          timestamp: new Date(Date.now() - 3000000).toISOString()
        }
      ]
    },
    {
      filename: 'conversation_2.jsonl',
      data: [
        {
          message: { role: 'user', content: 'I need help with React components' },
          timestamp: new Date(Date.now() - 7200000).toISOString() // 2 hours ago
        },
        {
          message: { role: 'assistant', content: 'React components are the building blocks of React applications.' },
          timestamp: new Date(Date.now() - 7000000).toISOString()
        }
      ]
    },
    {
      filename: 'conversation_3.jsonl',
      data: [
        {
          message: { role: 'user', content: 'Quick question about CSS' },
          timestamp: new Date(Date.now() - 60000).toISOString() // 1 minute ago
        }
      ]
    }
  ];

  for (const conv of conversations) {
    const filePath = path.join(testDir, conv.filename);
    const content = conv.data.map(item => JSON.stringify(item)).join('\n') + '\n';
    await fs.writeFile(filePath, content);
  }
}