"""
Matching API Routes
Candidate-Vacancy matching and auto-application
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
import re
import unicodedata

from app.core.database import get_db
from app.core.database_async import get_async_db
from app.core.config import settings
from app.models.schemas import (
    MatchResult, MatchingResponse, 
    ApplicationCreate, ApplicationResponse, SemanticMatchingResponse, SemanticMatchItem
)
from app.models.entities import Candidate, Vacancy
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.vacancy_repository import VacancyRepository
from app.repositories.application_repository import ApplicationRepository
from app.agents.matching_agent import match_candidate_to_vacancy
from app.services.matching import MatchingService

router = APIRouter()


def _normalize_location_key(location: str | None) -> str:
    raw = (location or "").strip().lower()
    if not raw:
        return ""

    normalized = unicodedata.normalize("NFD", raw)
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    normalized = re.sub(r"[^a-z\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    aliases = {
        "bogota": {"bogota", "bogota dc", "bogota d c", "bta"},
        "medellin": {"medellin", "medallo", "med"},
        "cali": {"cali", "santiago de cali"},
        "barranquilla": {"barranquilla", "bquilla", "baq"},
        "bucaramanga": {"bucaramanga", "bga"},
    }

    for canonical, values in aliases.items():
        for value in values:
            if normalized == value or value in normalized:
                return canonical

    return normalized


def _canonical_location_label(location_key: str) -> str:
    mapping = {
        "bogota": "Bogota",
        "medellin": "Medellin",
        "cali": "Cali",
        "barranquilla": "Barranquilla",
        "bucaramanga": "Bucaramanga",
    }
    return mapping.get(location_key, "Bogota")


async def _build_semantic_response(
    candidate_id: int,
    db: AsyncSession,
    limit: int,
) -> SemanticMatchingResponse:
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        matches = await MatchingService.get_best_matches(db, candidate, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    engine = "sqlite" if settings.USE_SQLITE else "pgvector"
    items = [
        SemanticMatchItem(
            vacancy_id=vacancy.id,
            title=vacancy.title,
            company=vacancy.company,
            similarity_score=round(similarity_score, 2),
            work_modality=vacancy.work_modality,
            location=vacancy.location,
        )
        for vacancy, similarity_score in matches
    ]

    return SemanticMatchingResponse(
        candidate_id=candidate_id,
        total_matches=len(items),
        matches=items,
        status="success",
        engine=engine,
    )


@router.get("/semantic-match/{candidate_id}")
async def get_semantic_matches_for_candidate_v2(
    candidate_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Semantic matching endpoint that chooses SQLite text matching or pgvector semantic matching.
    """
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")

    response = await _build_semantic_response(candidate_id, db, limit)
    return {
        "status": response.status,
        "engine": response.engine,
        "data": [item.model_dump() for item in response.matches],
    }


@router.post("/semantic/{candidate_id}", response_model=SemanticMatchingResponse)
async def get_semantic_matches_for_candidate(
    candidate_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Backward-compatible semantic matching endpoint used by the current frontend.
    """
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")

    return await _build_semantic_response(candidate_id, db, limit)

@router.get("/candidate/{candidate_id}", response_model=MatchingResponse)
async def get_matches_for_candidate(
    candidate_id: int,
    min_score: float = 0.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recommended vacancies for a candidate with match percentages
    Uses LangGraph matching agent for scoring
    Filters strictly by candidate location
    """
    candidate_repo = CandidateRepository(db)
    vacancy_repo = VacancyRepository(db)
    
    candidate = candidate_repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get all active vacancies
    all_vacancies = vacancy_repo.get_all(active_only=True)
    
    # Strict filter by canonical location (supports equivalent spellings)
    candidate_location_key = _normalize_location_key(candidate.location)
    if candidate_location_key:
        vacancies = [
            v for v in all_vacancies
            if _normalize_location_key(v.location) == candidate_location_key
        ]

        # Self-heal legacy dataset rows generated before location normalization improvements.
        if not vacancies:
            marker = f"[AUTO_DATASET_CANDIDATE:{candidate_id}]"
            auto_rows = db.query(Vacancy).filter(Vacancy.description.contains(marker)).all()
            if auto_rows:
                canonical_label = _canonical_location_label(candidate_location_key)
                for row in auto_rows:
                    row.location = canonical_label
                db.commit()

                all_vacancies = vacancy_repo.get_all(active_only=True)
                vacancies = [
                    v for v in all_vacancies
                    if _normalize_location_key(v.location) == candidate_location_key
                ]
    else:
        vacancies = all_vacancies
    
    # Calculate matches
    matches = []
    for vacancy in vacancies:
        # Run matching algorithm
        result = match_candidate_to_vacancy(
            candidate_skills=candidate.skills or [],
            candidate_experience=candidate.experience_years or 0,
            candidate_salary=candidate.expected_salary,
            candidate_modality=candidate.work_modality,
            candidate_location=candidate.location,
            vacancy_skills=vacancy.required_skills or [],
            vacancy_experience=vacancy.experience_required or 0,
            vacancy_salary_min=vacancy.salary_min,
            vacancy_salary_max=vacancy.salary_max,
            vacancy_modality=vacancy.work_modality,
            vacancy_location=vacancy.location
        )
        
        if result["total_score"] >= min_score:
            salary_range = f"${vacancy.salary_min or 0:,.0f} - ${vacancy.salary_max or 0:,.0f}"
            
            matches.append(MatchResult(
                vacancy_id=vacancy.id,
                title=vacancy.title,
                company=vacancy.company,
                match_score=result["total_score"],
                salary_range=salary_range,
                work_modality=vacancy.work_modality,
                location=vacancy.location,
                matching_skills=result["matching_skills"],
                missing_skills=result["missing_skills"]
            ))
    
    # Sort by score descending and limit
    matches.sort(key=lambda x: x.match_score, reverse=True)
    matches = matches[:limit]
    
    return MatchingResponse(
        candidate_id=candidate_id,
        candidate_name=candidate.full_name,
        total_matches=len(matches),
        matches=matches
    )

@router.post("/apply", response_model=ApplicationResponse)
async def apply_to_vacancy(data: ApplicationCreate, db: Session = Depends(get_db)):
    """
    Auto-apply candidate to a vacancy
    Calculates match score and saves application
    """
    candidate_repo = CandidateRepository(db)
    vacancy_repo = VacancyRepository(db)
    application_repo = ApplicationRepository(db)
    
    # Validate candidate
    candidate = candidate_repo.get_by_id(data.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Validate vacancy
    vacancy = vacancy_repo.get_by_id(data.vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    if not vacancy.is_active:
        raise HTTPException(status_code=400, detail="Vacancy is no longer active")
    
    # Check if already applied
    if application_repo.exists(data.candidate_id, data.vacancy_id):
        raise HTTPException(status_code=400, detail="Already applied to this vacancy")
    
    # Calculate match score
    result = match_candidate_to_vacancy(
        candidate_skills=candidate.skills or [],
        candidate_experience=candidate.experience_years or 0,
        candidate_salary=candidate.expected_salary,
        candidate_modality=candidate.work_modality,
        candidate_location=candidate.location,
        vacancy_skills=vacancy.required_skills or [],
        vacancy_experience=vacancy.experience_required or 0,
        vacancy_salary_min=vacancy.salary_min,
        vacancy_salary_max=vacancy.salary_max,
        vacancy_modality=vacancy.work_modality,
        vacancy_location=vacancy.location
    )
    
    # Create application
    application = application_repo.create(
        candidate_id=data.candidate_id,
        vacancy_id=data.vacancy_id,
        match_score=Decimal(str(result["total_score"]))
    )
    
    return ApplicationResponse(
        id=application.id,
        candidate_id=application.candidate_id,
        vacancy_id=application.vacancy_id,
        match_score=application.match_score,
        status=application.status,
        applied_at=application.applied_at,
        vacancy_title=vacancy.title,
        company=vacancy.company
    )

@router.get("/applications/candidate/{candidate_id}", response_model=List[ApplicationResponse])
async def get_candidate_applications(candidate_id: int, db: Session = Depends(get_db)):
    """Get all applications for a candidate"""
    application_repo = ApplicationRepository(db)
    applications = application_repo.get_by_candidate(candidate_id)
    
    result = []
    for app in applications:
        result.append(ApplicationResponse(
            id=app.id,
            candidate_id=app.candidate_id,
            vacancy_id=app.vacancy_id,
            match_score=app.match_score,
            status=app.status,
            applied_at=app.applied_at,
            vacancy_title=app.vacancy.title if app.vacancy else None,
            company=app.vacancy.company if app.vacancy else None
        ))
    
    return result

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update application status"""
    valid_statuses = ["pending", "reviewed", "interviewed", "accepted", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    application_repo = ApplicationRepository(db)
    application = application_repo.update_status(application_id, status)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": f"Application status updated to {status}"}
