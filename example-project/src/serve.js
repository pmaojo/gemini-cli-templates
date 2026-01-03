/**
 * ML Model Serving API
 * Built following ml-engineer agent guidelines (gemini-3-flash)
 * 
 * Features:
 * - RESTful prediction API
 * - Model versioning support
 * - Request/response logging
 * - Health check endpoint
 * - Latency monitoring
 */

import { createServer } from 'http';
import { readFileSync, existsSync } from 'fs';

const PORT = 3000;

// ============================================
// LOAD MODEL
// ============================================
function loadModel() {
  const modelPath = './models/model_latest.json';
  
  if (!existsSync(modelPath)) {
    console.error('❌ No model found! Run "npm run train" first.');
    process.exit(1);
  }
  
  const model = JSON.parse(readFileSync(modelPath, 'utf8'));
  console.log(`📦 Loaded model v${model.metadata.version}`);
  console.log(`   Trained: ${model.metadata.trainedAt}`);
  console.log(`   RMSE: $${model.metadata.metrics.finalRMSE.toFixed(2)}`);
  
  return model;
}

// ============================================
// PREDICTION
// ============================================
function predict(model, features) {
  const { weights, bias } = model;
  
  const prediction = 
    weights.sqft * (features.sqft || 0) +
    weights.bedrooms * (features.bedrooms || 0) +
    weights.bathrooms * (features.bathrooms || 0) +
    weights.age * (features.age || 0) +
    bias;
  
  return Math.max(0, prediction); // Ensure non-negative price
}

// ============================================
// METRICS (Monitoring)
// ============================================
const metrics = {
  requestCount: 0,
  totalLatency: 0,
  predictions: [],
  errors: 0
};

function recordMetrics(latency, prediction) {
  metrics.requestCount++;
  metrics.totalLatency += latency;
  metrics.predictions.push({
    timestamp: new Date().toISOString(),
    prediction,
    latency
  });
  
  // Keep only last 100 predictions for memory
  if (metrics.predictions.length > 100) {
    metrics.predictions.shift();
  }
}

// ============================================
// HTTP SERVER
// ============================================
const model = loadModel();

const server = createServer((req, res) => {
  const startTime = Date.now();
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // Health check
  if (url.pathname === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'healthy',
      model: model.metadata.version,
      uptime: process.uptime()
    }));
    return;
  }
  
  // Metrics endpoint
  if (url.pathname === '/metrics') {
    res.writeHead(200);
    res.end(JSON.stringify({
      requestCount: metrics.requestCount,
      avgLatencyMs: metrics.requestCount > 0 
        ? (metrics.totalLatency / metrics.requestCount).toFixed(2) 
        : 0,
      errorCount: metrics.errors,
      recentPredictions: metrics.predictions.slice(-10)
    }));
    return;
  }
  
  // Model info
  if (url.pathname === '/model') {
    res.writeHead(200);
    res.end(JSON.stringify(model.metadata));
    return;
  }
  
  // Prediction endpoint
  if (url.pathname === '/predict') {
    try {
      const features = {
        sqft: parseFloat(url.searchParams.get('sqft')) || 1500,
        bedrooms: parseFloat(url.searchParams.get('bedrooms')) || 3,
        bathrooms: parseFloat(url.searchParams.get('bathrooms')) || 2,
        age: parseFloat(url.searchParams.get('age')) || 10
      };
      
      const prediction = predict(model, features);
      const latency = Date.now() - startTime;
      
      recordMetrics(latency, prediction);
      
      res.writeHead(200);
      res.end(JSON.stringify({
        prediction: Math.round(prediction),
        formatted: `$${Math.round(prediction).toLocaleString()}`,
        features,
        model: model.metadata.version,
        latencyMs: latency
      }));
      
      console.log(`🎯 Prediction: $${Math.round(prediction).toLocaleString()} (${latency}ms)`);
      
    } catch (error) {
      metrics.errors++;
      res.writeHead(400);
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  
  // Default: API info
  res.writeHead(200);
  res.end(JSON.stringify({
    name: 'ML Model Serving API',
    version: '1.0.0',
    agent: 'ml-engineer',
    model: 'gemini-3-flash',
    endpoints: {
      '/predict': 'GET - Make a prediction (params: sqft, bedrooms, bathrooms, age)',
      '/health': 'GET - Health check',
      '/metrics': 'GET - Request metrics',
      '/model': 'GET - Model metadata'
    },
    example: '/predict?sqft=2000&bedrooms=4&bathrooms=3&age=5'
  }));
});

server.listen(PORT, () => {
  console.log('\n═══════════════════════════════════════════');
  console.log('🚀 ML Model Serving API Started!');
  console.log('   Agent: ml-engineer | Model: gemini-3-flash');
  console.log('═══════════════════════════════════════════\n');
  console.log(`📡 Server: http://localhost:${PORT}`);
  console.log(`🎯 Predict: http://localhost:${PORT}/predict?sqft=2000&bedrooms=4&bathrooms=3&age=5`);
  console.log(`❤️  Health: http://localhost:${PORT}/health`);
  console.log(`📊 Metrics: http://localhost:${PORT}/metrics`);
  console.log('\nPress Ctrl+C to stop.\n');
});
