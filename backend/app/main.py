# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Aplicacion FastAPI principal. Partes: lifespan para inicializar tablas, CORS, registro de routers, endpoint raiz, health de API/DB y diagnostico de IA.

"""
GraphHired Backend - Main Application Entry Point
FastAPI application with Clean Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.api.routes import logs, candidates, vacancies, matching, auth, agents, applications

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    init_db()
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(logs.router, prefix="/api/logs", tags=["Logs - PoC"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(vacancies.router, prefix="/api/vacancies", tags=["Vacancies"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])

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
    database_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception as exc:
        database_status = f"error: {exc.__class__.__name__}"
    finally:
        try:
            db.close()
        except Exception:
            pass

    return {
        "status": "healthy" if database_status == "connected" else "degraded",
        "database": database_status,
        "ai_service": "ready" if settings.OPENAI_API_KEY else "missing_api_key"
    }

@app.get("/health/ai", tags=["Health"])
async def ai_health_check():
    """AI provider diagnostics without exposing secrets"""
    return {
        "provider": "openai",
        "model": settings.OPENAI_MODEL,
        "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        "api_key_configured": bool(settings.OPENAI_API_KEY)
    }
