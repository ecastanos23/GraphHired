# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Rutas de la PoC tecnica. Partes: procesar texto, persistir log y consultar registros para validar UI/API/DB.

"""
Logs API Routes - PoC Endpoint
Hello World test for LangGraph integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import sanitize_text
from app.models.schemas import LogCreate, LogResponse
from app.repositories.log_repository import LogRepository
from app.agents.poc_agent import process_text

router = APIRouter()

@router.post("/process", response_model=LogResponse)
async def process_and_log(data: LogCreate, db: Session = Depends(get_db)):
    """
    PoC Endpoint: Receives text, processes through LangGraph, saves to DB
    
    This endpoint demonstrates:
    1. Text input reception
    2. Sanitization (OWASP)
    3. LangGraph node processing (uppercase transformation)
    4. Database persistence
    """
    # Sanitize input
    clean_text = sanitize_text(data.input_text)
    
    if not clean_text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    # Process through LangGraph (uppercase transformation)
    output_text = process_text(clean_text)
    
    # Save to database
    repo = LogRepository(db)
    log = repo.create(input_text=clean_text, output_text=output_text)
    
    return log

@router.get("/", response_model=List[LogResponse])
async def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Get all log entries"""
    repo = LogRepository(db)
    return repo.get_all(limit=limit)

@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """Get specific log entry by ID"""
    repo = LogRepository(db)
    log = repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
