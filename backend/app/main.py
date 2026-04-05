"""
GraphHired Backend - Main Application Entry Point
FastAPI application with Clean Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import logs, candidates, vacancies, matching

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Starting GraphHired API...")
    yield
    print("👋 Shutting down GraphHired API...")

app = FastAPI(
    title="GraphHired API",
    description="AI-powered job matching platform using LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(logs.router, prefix="/api/logs", tags=["Logs - PoC"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(vacancies.router, prefix="/api/vacancies", tags=["Vacancies"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GraphHired API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "ready"
    }

@app.get("/health/ai", tags=["Health"])
async def ai_health_check():
    """AI provider diagnostics without exposing secrets"""
    return {
        "provider": "gemini",
        "model": settings.GEMINI_MODEL,
        "embedding_model": settings.GEMINI_EMBEDDING_MODEL,
        "api_key_configured": bool(settings.GEMINI_API_KEY)
    }
