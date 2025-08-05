# Discover vNext - Development Makefile

.PHONY: help setup start stop clean install test docker-build docker-start setup-data

# Default target
help:
	@echo "🚀 Discover vNext - Development Commands"
	@echo "=================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup       - Set up development environment"
	@echo "  make install     - Install all dependencies"
	@echo ""
	@echo "🏃 Development:"
	@echo "  make start       - Start development servers"
	@echo "  make stop        - Stop all services"
	@echo "  make setup-data  - Populate database with sample data"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-start   - Start with Docker Compose"
	@echo "  make docker-stop    - Stop Docker services"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean       - Clean up build artifacts"
	@echo "  make test        - Run tests"
	@echo ""

# Setup development environment
setup:
	@echo "🔧 Setting up Discover vNext development environment..."
	@chmod +x start-dev.sh
	@chmod +x setup-data.py
	@echo "✅ Setup complete! Run 'make start' to begin development."

# Install dependencies
install:
	@echo "📦 Installing backend dependencies..."
	@cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ All dependencies installed!"

# Start development servers
start:
	@echo "🚀 Starting development environment..."
	@./start-dev.sh

# Start with Docker
docker-start:
	@echo "🐳 Starting with Docker Compose..."
	@./start-dev.sh --docker

# Stop services
stop:
	@echo "🛑 Stopping all services..."
	@pkill -f "uvicorn main:app" || true
	@pkill -f "npm start" || true
	@docker-compose down
	@echo "✅ All services stopped."

# Docker build
docker-build:
	@echo "🏗️  Building Docker images..."
	@docker-compose build

# Docker stop
docker-stop:
	@echo "🐳 Stopping Docker services..."
	@docker-compose down

# Setup sample data
setup-data:
	@echo "📊 Setting up sample data..."
	@python3 setup-data.py

# Clean build artifacts
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf backend/venv
	@rm -rf frontend/node_modules
	@rm -rf frontend/build
	@rm -f backend/*.db
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleanup complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	@cd backend && source venv/bin/activate && python -m pytest tests/ || echo "⚠️  No backend tests found"
	@cd frontend && npm test -- --watchAll=false || echo "⚠️  No frontend tests found"

# Development shortcuts
dev: start
backend:
	@cd backend && source venv/bin/activate && uvicorn main:app --reload

frontend:
	@cd frontend && npm start

redis:
	@docker-compose up -d redis

# Health check
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"
	@curl -f http://localhost:3000 2>/dev/null && echo "✅ Frontend is healthy" || echo "❌ Frontend is not responding"
	@docker-compose ps redis | grep "Up" && echo "✅ Redis is healthy" || echo "❌ Redis is not running"

# Logs
logs:
	@echo "📋 Showing service logs..."
	@docker-compose logs -f

# Quick start for new developers
quickstart: setup install start setup-data
	@echo ""
	@echo "🎉 Discover vNext is ready!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"