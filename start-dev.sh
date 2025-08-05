#!/bin/bash

# Discover vNext - Development Startup Script

set -e

echo "🚀 Starting Discover vNext Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists in backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating backend/.env file from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your OpenAI API key before proceeding."
    echo "   OPENAI_API_KEY=your_api_key_here"
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 3

# Check if we should run with Docker or locally
if [ "$1" = "--docker" ]; then
    echo "🐳 Starting all services with Docker..."
    docker-compose up --build
else
    echo "💻 Starting services locally..."
    
    # Start backend
    echo "🔧 Starting FastAPI backend..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Start backend in background
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
    
    cd ..
    
    # Start frontend
    echo "⚛️  Starting React frontend..."
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    
    # Start frontend in background
    npm start &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
    
    cd ..
    
    echo ""
    echo "🎉 Development environment is starting up!"
    echo ""
    echo "📋 Services:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "🔧 Development Tips:"
    echo "   - Backend logs: tail -f backend/logs/*.log"
    echo "   - Frontend will auto-reload on file changes"
    echo "   - Backend will auto-reload on file changes"
    echo "   - Press Ctrl+C to stop all services"
    echo ""
    
    # Function to cleanup on exit
    cleanup() {
        echo ""
        echo "🛑 Shutting down services..."
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        if [ ! -z "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        docker-compose down
        echo "✅ All services stopped."
    }
    
    # Set trap to cleanup on script exit
    trap cleanup EXIT
    
    # Wait for user interrupt
    wait
fi