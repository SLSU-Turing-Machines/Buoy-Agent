#!/bin/bash

# Exit on any error
set -e

# === Step 1: Build Svelte frontend ===
echo "📦 Building Svelte frontend..."
cd svelte
npm run build
cd ..

# === Step 2: Copy build output to ICP assets (optional) ===
echo "📁 Syncing Svelte build to src/buoy-ai-frontend/assets/..."
rm -rf src/buoy-ai-frontend/assets/*
cp -r svelte/build/* src/buoy-ai-frontend/assets/

# === Step 3: Deploy to Internet Computer ===
echo "🚀 Deploying to Internet Computer..."
dfx deploy

# === Step 4: Run Python Flask API ===
echo "🐍 Starting Flask server..."
cd app

source ../.venv/bin/activate
python app.py
