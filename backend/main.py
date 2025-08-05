from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from models.database import engine, Base
from models import get_db
from routers import (
    companies_router,
    users_router,
    search_router,
    recommendations_router,
    documents_router
)

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI app
    """
    # Startup: Create database tables
    print("🚀 Starting Discover vNext API...")
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Discover vNext API...")


# Create FastAPI app
app = FastAPI(
    title="Discover vNext API",
    description="A powerful recommendation engine API for testing and simulating Discover-style document recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Discover vNext - Recommendation Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "discover-vnext-api",
        "version": "1.0.0"
    }


@app.get("/api/status")
async def api_status(db=Depends(get_db)):
    """Detailed API status with database connectivity"""
    try:
        # Test database connection
        from models.models import Company
        company_count = db.query(Company).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "companies": company_count,
            "endpoints": {
                "companies": "/api/companies",
                "users": "/api/users", 
                "search": "/api/search",
                "recommendations": "/api/recommendations",
                "documents": "/api/documents"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )