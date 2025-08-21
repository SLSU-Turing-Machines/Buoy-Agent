#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting build and deploy..."

# === Detect project root ===
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# === Ensure .env exists ===
if [ ! -f .env ]; then
  read -p "No Environment Variable Found. Enter your token: " token
  echo "buoy=$token" > .env
  echo ".env file created ✅"
fi

# === Build Svelte frontend ===
echo "📦 Building Svelte frontend..."
cd svelte

# --- Ensure nvm & Node.js are available ---
if ! command -v node >/dev/null 2>&1; then
  echo "⚠️ Node.js is not installed. Installing nvm + Node.js..."

  # Install nvm if missing
  if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
  fi

  # Load nvm
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

  # Install and use Node.js 20.x
  nvm install 20
  nvm use 20
else
  echo "✅ Node.js already installed: $(node -v)"
fi

# --- Load nvm in case it’s not yet sourced ---
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# --- Install dependencies ---
if [ ! -d node_modules ]; then
  echo "📥 Installing Node.js dependencies..."
  npm install
fi

# --- Build project ---
npm run build
echo "✅ Svelte frontend built successfully."

cd "$PROJECT_ROOT"

# === Step 2: Copy build output to ICP assets (optional) ===
echo "📁 Syncing Svelte build to src/buoy-ai-frontend/assets/..."
rm -rf src/buoy-ai-frontend/assets/*
cp -r svelte/build/* src/buoy-ai-frontend/assets/
# == Check if rust/cargo is installed ==
if ! command -v cargo >/dev/null 2>&1; then
  echo "⚠️ Rust is not installed. Installing..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  source "$HOME/.cargo/env"
else
  echo "✅ Rust and Cargo are installed: $(cargo --version)"
fi

# === check for gcc cc compiler ===
if ! command -v gcc >/dev/null 2>&1; then
  echo "⚠️ GCC is not installed. Installing required build tools..."
  sudo apt update
  sudo apt install -y build-essential pkg-config libssl-dev
else
  echo "✅ GCC is installed:"
  gcc --version | head -n 1
fi




# === Step 3: Deploy to Internet Computer ===
echo "🚀 Deploying to Internet Computer..."
dfx start --background
dfx deploy 
dfx canister id buoy-ai-frontend
echo "✅ Deployed buoy-ai-frontend successfully @ http://127.0.0.1:4943/?canisterId=$(dfx canister id buoy-ai-frontend)"

# === Step 4: Run Python Flask API ===
echo "🐍 Starting Flask server..."
cd app
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
python app.py

# on close
deactivate
dfx stop --background

# on any error close
if [ $? -ne 0 ]; then
  echo "❌ An error occurred. Stopping services..."
  deactivate
  dfx stop --background
  exit 1
fi