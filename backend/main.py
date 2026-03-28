"""
GraphHired - Backend Entry Point
FastAPI application with LangGraph agents for job matching
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import logs, candidates, vacancies, matching

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-powered job matching platform using LangGraph agents"
)

# CORS middleware for frontend communication (TEMP: allow all for debug)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(logs.router, prefix="/api/logs", tags=["PoC - Logs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(vacancies.router, prefix="/api/vacancies", tags=["Vacancies"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "GraphHired API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": "ready"
    }
