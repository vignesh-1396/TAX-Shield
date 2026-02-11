#!/bin/bash

# Portable Startup Script for Mac

echo "🚀 Starting ITC Protection System (Portable Mode)..."

# 1. Setup Backend
echo "📦 Setting up Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Start Backend in background
echo "🟢 Starting Key-Value Store (Backend) on port 8000..."
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 2. Setup Frontend
echo "📦 Setting up Frontend..."
cd ../frontend/itc-shield
if [ ! -d "node_modules" ]; then
    echo "Installing node modules..."
    npm install
fi

# Start Frontend
echo "🟢 Starting Dashboard (Frontend) on port 3000..."
npm run dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID; kill $FRONTEND_PID" EXIT

echo "✅ System Running!"
echo "➡️  Open http://localhost:3000 in your browser."
echo "Press Ctrl+C to stop servers."

wait
