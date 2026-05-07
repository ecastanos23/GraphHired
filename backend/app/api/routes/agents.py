# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Rutas de agentes. Partes: consulta de timeline agentico y refresco manual del dataset de vacantes para un candidato.

"""Agent trace and orchestration endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.agents.profile_agent import analyze_profile
from app.agents.vacancy_agent import sync_curated_market_vacancies
from app.core.database import get_db
from app.models.schemas import AgentEventResponse
from app.repositories.agent_event_repository import AgentEventRepository
from app.repositories.candidate_repository import CandidateRepository

router = APIRouter()


@router.get("/trace", response_model=List[AgentEventResponse])
async def get_agent_trace(
    candidate_id: int = Query(..., gt=0),
    limit: int = Query(100, gt=0, le=200),
    db: Session = Depends(get_db),
):
    """
    Return the trace timeline for a candidate.
    
    Si el candidato no existe, retorna una lista vacía en lugar de 404.
    Esto hace el endpoint más resiliente para diagnósticos y datos ausentes.
    """
    # Verificar si el candidato existe
    candidate = CandidateRepository(db).get_by_id(candidate_id)
    
    # Si no existe, retornar lista vacía en lugar de error 404
    if not candidate:
        return []
    
    # Si existe, retornar su historial de eventos de agentes
    return AgentEventRepository(db).get_for_candidate(candidate_id, limit=limit)


@router.post("/vacancies/refresh")
async def refresh_curated_vacancies(candidate_id: int, db: Session = Depends(get_db)):
    """Run the Vacancy Agent manually for a candidate."""
    candidate = CandidateRepository(db).get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.cv_text:
        raise HTTPException(status_code=400, detail="Candidate has no CV text")

    profile = analyze_profile(
        candidate.cv_text,
        {
            "salary": candidate.expected_salary,
            "modality": candidate.work_modality,
            "location": candidate.location,
        },
    )
    count = sync_curated_market_vacancies(
        db=db,
        candidate_id=candidate.id,
        cv_text=candidate.cv_text,
        profile_data=profile,
        preferred_location=candidate.location or "Bogota",
    )
    return {"status": "success", "created": count}
