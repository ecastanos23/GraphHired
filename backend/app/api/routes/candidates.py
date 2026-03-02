"""
Candidates API Routes
CV upload, profile management, and candidate operations
HU 01 - Entrada/Proceso/Salida del sistema
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import io

from app.core.database import get_db
from app.core.security import sanitize_text, sanitize_email, validate_file_type
from app.models.schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse, 
    CVUpload, ProfileAnalysis
)
from app.repositories.candidate_repository import CandidateRepository
from app.agents.profile_agent import analyze_profile

router = APIRouter()

@router.post("/", response_model=CandidateResponse)
async def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    """Register a new candidate"""
    repo = CandidateRepository(db)
    
    # Check if email already exists
    existing = repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Sanitize inputs
    data.full_name = sanitize_text(data.full_name)
    if data.cv_text:
        data.cv_text = sanitize_text(data.cv_text)
    
    candidate = repo.create(data)
    return candidate

@router.post("/upload-cv", response_model=CandidateResponse)
@router.post("/upload_cv", response_model=CandidateResponse, include_in_schema=False)
async def upload_cv_with_expectations(data: CVUpload, db: Session = Depends(get_db)):
    """
    Upload CV with candidate expectations (salary, modality, location)
    HU 01 - 5.2 Proceso: Validar e invocar el agente de perfil
    Validates required fields and creates/updates candidate profile
    """
    repo = CandidateRepository(db)
    
    # Validate required fields (will highlight in red on frontend if missing)
    errors = []
    if not data.email:
        errors.append("email")
    if not data.full_name or len(data.full_name.strip()) < 2:
        errors.append("full_name")
    if not data.cv_text or len(data.cv_text.strip()) < 10:
        errors.append("cv_text")
    if data.expected_salary is None or data.expected_salary < 0:
        errors.append("expected_salary")
    if not data.work_modality:
        errors.append("work_modality")
    if not data.location:
        errors.append("location")
    
    if errors:
        raise HTTPException(
            status_code=422, 
            detail={"message": "Missing required fields", "fields": errors}
        )
    
    # Check if candidate exists
    existing = repo.get_by_email(data.email)
    
    # Sanitize inputs
    clean_name = sanitize_text(data.full_name)
    clean_cv = sanitize_text(data.cv_text)
    clean_location = sanitize_text(data.location)
    
    if existing:
        # Update existing candidate
        existing.full_name = clean_name
        existing.cv_text = clean_cv
        existing.expected_salary = data.expected_salary
        existing.work_modality = data.work_modality
        existing.location = clean_location
        
        # 5.2 Proceso: Invocar agente de perfil con expectativas
        expectations = {
            "salary": data.expected_salary,
            "modality": data.work_modality,
            "location": clean_location
        }
        profile = analyze_profile(clean_cv, expectations)
        existing.skills = profile["skills"]
        existing.experience_years = profile["experience_years"]
        
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new candidate
        candidate_data = CandidateCreate(
            email=data.email,
            full_name=clean_name,
            cv_text=clean_cv,
            expected_salary=data.expected_salary,
            work_modality=data.work_modality,
            location=clean_location
        )
        candidate = repo.create(candidate_data)
        
        # 5.2 Proceso: Invocar agente de perfil con expectativas
        expectations = {
            "salary": data.expected_salary,
            "modality": data.work_modality,
            "location": clean_location
        }
        profile = analyze_profile(clean_cv, expectations)
        repo.update_profile(
            candidate.id,
            skills=profile["skills"],
            experience_years=profile["experience_years"]
        )
        
        db.refresh(candidate)
        return candidate

@router.get("/", response_model=List[CandidateResponse])
async def get_candidates(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all candidates with pagination"""
    repo = CandidateRepository(db)
    return repo.get_all(skip=skip, limit=limit)

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate by ID"""
    repo = CandidateRepository(db)
    candidate = repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/{candidate_id}/analysis", response_model=ProfileAnalysis)
async def analyze_candidate_profile(candidate_id: int, db: Session = Depends(get_db)):
    """Run AI analysis on candidate's CV"""
    repo = CandidateRepository(db)
    candidate = repo.get_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.cv_text:
        raise HTTPException(status_code=400, detail="No CV text available for analysis")
    
    profile = analyze_profile(candidate.cv_text)
    
    # Update candidate with extracted data
    repo.update_profile(
        candidate_id,
        skills=profile["skills"],
        experience_years=profile["experience_years"]
    )
    
    return ProfileAnalysis(**profile)

@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int, 
    data: CandidateUpdate, 
    db: Session = Depends(get_db)
):
    """Update candidate information"""
    repo = CandidateRepository(db)
    
    if data.full_name:
        data.full_name = sanitize_text(data.full_name)
    if data.cv_text:
        data.cv_text = sanitize_text(data.cv_text)
    
    candidate = repo.update(candidate_id, data)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete candidate"""
    repo = CandidateRepository(db)
    if not repo.delete(candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted successfully"}
