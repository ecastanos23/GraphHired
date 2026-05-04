# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Rutas de vacantes. Partes: creacion, listado, busqueda, consulta por id, desactivacion y eliminacion de vacantes.

"""
Vacancies API Routes
Job vacancy management and search
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.security import sanitize_text
from app.models.schemas import VacancyCreate, VacancyResponse
from app.repositories.vacancy_repository import VacancyRepository

router = APIRouter()

@router.post("/", response_model=VacancyResponse)
async def create_vacancy(data: VacancyCreate, db: Session = Depends(get_db)):
    """Create a new job vacancy"""
    repo = VacancyRepository(db)
    
    # Sanitize inputs
    data.title = sanitize_text(data.title)
    data.company = sanitize_text(data.company)
    data.description = sanitize_text(data.description)
    data.required_skills = [sanitize_text(s) for s in data.required_skills]
    
    vacancy = repo.create(data)
    return vacancy

@router.get("/", response_model=List[VacancyResponse])
async def get_vacancies(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all vacancies with pagination"""
    repo = VacancyRepository(db)
    return repo.get_all(skip=skip, limit=limit, active_only=active_only)

@router.get("/search", response_model=List[VacancyResponse])
async def search_vacancies(
    work_modality: Optional[str] = Query(None, pattern="^(remote|hybrid|onsite)$"),
    min_salary: Optional[Decimal] = None,
    max_experience: Optional[int] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search vacancies by criteria"""
    repo = VacancyRepository(db)
    
    if location:
        location = sanitize_text(location)
    
    return repo.search_by_criteria(
        work_modality=work_modality,
        min_salary=min_salary,
        max_experience=max_experience,
        location=location
    )

@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    """Get vacancy by ID"""
    repo = VacancyRepository(db)
    vacancy = repo.get_by_id(vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy

@router.put("/{vacancy_id}/deactivate")
async def deactivate_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    """Deactivate a vacancy"""
    repo = VacancyRepository(db)
    if not repo.deactivate(vacancy_id):
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return {"message": "Vacancy deactivated successfully"}

@router.delete("/{vacancy_id}")
async def delete_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    """Delete vacancy"""
    repo = VacancyRepository(db)
    if not repo.delete(vacancy_id):
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return {"message": "Vacancy deleted successfully"}
