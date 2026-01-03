/**
 * ML Model Training Pipeline
 * Built following ml-engineer agent guidelines (gemini-3-flash)
 * 
 * Features:
 * - Simple baseline model (linear regression)
 * - Data versioning with timestamps
 * - Model serialization
 * - Training metrics logging
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs';

// ============================================
// TRAINING DATA (Feature Engineering)
// ============================================
const trainingData = {
  version: '1.0.0',
  timestamp: new Date().toISOString(),
  features: ['sqft', 'bedrooms', 'bathrooms', 'age'],
  samples: [
    { sqft: 1500, bedrooms: 3, bathrooms: 2, age: 10, price: 350000 },
    { sqft: 2000, bedrooms: 4, bathrooms: 3, age: 5, price: 500000 },
    { sqft: 1200, bedrooms: 2, bathrooms: 1, age: 20, price: 250000 },
    { sqft: 1800, bedrooms: 3, bathrooms: 2, age: 8, price: 420000 },
    { sqft: 2500, bedrooms: 5, bathrooms: 4, age: 2, price: 650000 },
    { sqft: 1000, bedrooms: 1, bathrooms: 1, age: 30, price: 180000 },
    { sqft: 2200, bedrooms: 4, bathrooms: 3, age: 3, price: 550000 },
    { sqft: 1600, bedrooms: 3, bathrooms: 2, age: 15, price: 320000 },
  ]
};

// ============================================
// MODEL TRAINING (Linear Regression)
// ============================================
function trainModel(data) {
  console.log('🚀 Starting model training...');
  console.log(`📊 Training samples: ${data.samples.length}`);
  console.log(`📋 Features: ${data.features.join(', ')}`);
  
  // Simple linear model: price = w1*sqft + w2*bedrooms + w3*bathrooms - w4*age + bias
  // Using gradient descent (simplified implementation)
  
  let weights = { sqft: 0.1, bedrooms: 10000, bathrooms: 15000, age: -1000 };
  let bias = 50000;
  const learningRate = 0.0000001;
  const epochs = 1000;
  
  const startTime = Date.now();
  
  for (let epoch = 0; epoch < epochs; epoch++) {
    let totalLoss = 0;
    
    for (const sample of data.samples) {
      // Forward pass
      const prediction = 
        weights.sqft * sample.sqft +
        weights.bedrooms * sample.bedrooms +
        weights.bathrooms * sample.bathrooms +
        weights.age * sample.age +
        bias;
      
      const error = prediction - sample.price;
      totalLoss += error ** 2;
      
      // Backward pass (gradient descent)
      weights.sqft -= learningRate * error * sample.sqft;
      weights.bedrooms -= learningRate * error * sample.bedrooms * 100;
      weights.bathrooms -= learningRate * error * sample.bathrooms * 100;
      weights.age -= learningRate * error * sample.age;
      bias -= learningRate * error;
    }
    
    if (epoch % 200 === 0) {
      const avgLoss = Math.sqrt(totalLoss / data.samples.length);
      console.log(`  Epoch ${epoch}: RMSE = $${avgLoss.toFixed(2)}`);
    }
  }
  
  const trainingTime = Date.now() - startTime;
  const finalLoss = Math.sqrt(data.samples.reduce((sum, s) => {
    const pred = weights.sqft * s.sqft + weights.bedrooms * s.bedrooms + 
                 weights.bathrooms * s.bathrooms + weights.age * s.age + bias;
    return sum + (pred - s.price) ** 2;
  }, 0) / data.samples.length);
  
  return {
    weights,
    bias,
    metadata: {
      version: '1.0.0',
      trainedAt: new Date().toISOString(),
      dataVersion: data.version,
      samplesCount: data.samples.length,
      features: data.features,
      metrics: {
        finalRMSE: finalLoss,
        trainingTimeMs: trainingTime,
        epochs: epochs
      }
    }
  };
}

// ============================================
// SAVE MODEL (with versioning)
// ============================================
function saveModel(model) {
  const modelsDir = './models';
  if (!existsSync(modelsDir)) {
    mkdirSync(modelsDir, { recursive: true });
  }
  
  const modelPath = `${modelsDir}/model_v${model.metadata.version}.json`;
  const latestPath = `${modelsDir}/model_latest.json`;
  
  writeFileSync(modelPath, JSON.stringify(model, null, 2));
  writeFileSync(latestPath, JSON.stringify(model, null, 2));
  
  console.log(`\n✅ Model saved to: ${modelPath}`);
  console.log(`📁 Latest symlink: ${latestPath}`);
  
  return modelPath;
}

// ============================================
// MAIN
// ============================================
console.log('═══════════════════════════════════════════');
console.log('🤖 ML Training Pipeline - Gemini CLI Demo');
console.log('   Agent: ml-engineer | Model: gemini-3-flash');
console.log('═══════════════════════════════════════════\n');

const model = trainModel(trainingData);
saveModel(model);

console.log('\n📊 Model Metrics:');
console.log(`   RMSE: $${model.metadata.metrics.finalRMSE.toFixed(2)}`);
console.log(`   Training Time: ${model.metadata.metrics.trainingTimeMs}ms`);
console.log(`   Epochs: ${model.metadata.metrics.epochs}`);

console.log('\n🎯 Model Weights:');
Object.entries(model.weights).forEach(([feature, weight]) => {
  console.log(`   ${feature}: ${weight.toFixed(4)}`);
});
console.log(`   bias: ${model.bias.toFixed(4)}`);

console.log('\n✨ Training complete! Run "npm run serve" to start the API.');
