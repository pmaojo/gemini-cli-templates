/**
 * Jest Configuration for Gemini CLI Templates Analytics
 * Phase 4: Testing & Optimization
 */
module.exports = {
  // Test environment
  testEnvironment: 'node',
  
  // Test file patterns
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js',
    '**/__tests__/**/*.js'
  ],
  
  // Coverage configuration
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/analytics/**/*.js',
    'src/analytics-web/**/*.js',
    '!src/analytics.log',
    '!src/analytics-web/index.html*',
    '!**/node_modules/**',
    '!**/coverage/**'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 13,
      functions: 18,
      lines: 18,
      statements: 18
    },
    './src/analytics/core/': {
      branches: 15,
      functions: 20,
      lines: 20,
      statements: 20
    }
  },
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
  // Module paths
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  
  // Transform files
  transform: {},
  
  // Test timeout
  testTimeout: 10000,
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Module name mapping for frontend tests
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/analytics-web/$1',
    '^@analytics/(.*)$': '<rootDir>/src/analytics/$1'
  },
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/',
    '/dist/'
  ],
  
  // Watch plugins
  // watchPlugins: [
  //   'jest-watch-typeahead/filename',
  //   'jest-watch-typeahead/testname'
  // ]
};