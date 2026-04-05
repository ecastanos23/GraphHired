"""
Candidates API Routes
CV upload, profile management, and candidate operations
HU 01 - Entrada/Proceso/Salida del sistema
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import re
import io
import os
import tempfile

from app.core.database import get_db
from app.core.security import sanitize_text, sanitize_email, validate_file_type
from app.models.schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse, 
    CVUpload, ProfileAnalysis, CVGraphAnalysisResponse, VacancyCreate
)
from app.models.entities import Vacancy
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.vacancy_repository import VacancyRepository
from app.agents.profile_agent import analyze_profile, generate_colombia_job_dataset
from app.agents.cv_profile_graph import cv_profile_graph

router = APIRouter()


AUTO_DATASET_MARKER = "[AUTO_DATASET_CANDIDATE:"


def _salary_string_to_decimals(salary_range: str) -> tuple[Decimal, Decimal]:
    values = re.findall(r"\d[\d\.]*", salary_range or "")
    parsed: list[Decimal] = []
    for value in values[:2]:
        clean = value.replace(".", "")
        if clean.isdigit():
            parsed.append(Decimal(clean))

    if len(parsed) == 2:
        low, high = sorted(parsed)
        return low, high
    if len(parsed) == 1:
        return parsed[0], parsed[0]
    return Decimal("3000000"), Decimal("5000000")


def _mode_to_db(mode: str) -> str:
    normalized = (mode or "").strip().lower()
    if normalized == "remoto":
        return "remote"
    if normalized == "hibrido":
        return "hybrid"
    return "onsite"


def _experience_from_title(title: str) -> int:
    title_lower = (title or "").lower()
    if "junior" in title_lower or "auxiliar" in title_lower:
        return 1
    if "senior" in title_lower or "lider" in title_lower or "líder" in title_lower:
        return 5
    if "gerente" in title_lower or "director" in title_lower:
        return 8
    return 3


def _sync_generated_market_vacancies(
    db: Session,
    candidate_id: int,
    cv_text: str,
    profile_data: dict,
    preferred_location: str,
) -> None:
    """Create a fresh 20-item realistic Colombia market dataset tied to one candidate."""
    marker = f"{AUTO_DATASET_MARKER}{candidate_id}]"

    db.query(Vacancy).filter(Vacancy.description.contains(marker)).delete(synchronize_session=False)

    dataset = generate_colombia_job_dataset(
        cv_text=cv_text,
        profile_data=profile_data,
        preferred_location=preferred_location,
    )

    vacancy_repo = VacancyRepository(db)
    for item in dataset[:20]:
        salary_min, salary_max = _salary_string_to_decimals(str(item.get("salary", "")))
        skills_owned = [str(skill).strip() for skill in item.get("skills_owned", []) if str(skill).strip()]
        skills_gap = [str(skill).strip() for skill in item.get("skills_to_develop", []) if str(skill).strip()]
        required_skills = list(dict.fromkeys((skills_owned + skills_gap)))

        vacancy_data = VacancyCreate(
            title=str(item.get("title", "Cargo no especificado")),
            company=str(item.get("company", "Empresa Colombia")),
            description=(
                f"{marker} Oferta sugerida por perfil CV. "
                f"Match estimado: {item.get('match_percentage', 55)}%. "
                f"Habilidades actuales: {', '.join(skills_owned)}. "
                f"Habilidades por fortalecer: {', '.join(skills_gap)}."
            ),
            required_skills=required_skills,
            salary_min=salary_min,
            salary_max=salary_max,
            work_modality=_mode_to_db(str(item.get("mode", "Presencial"))),
            location=str(item.get("location", preferred_location or "Bogota")),
            experience_required=_experience_from_title(str(item.get("title", ""))),
        )
        vacancy_repo.create(vacancy_data)


@router.post("/{candidate_id}/analyze-cv-pdf", response_model=CVGraphAnalysisResponse)
async def analyze_cv_pdf_with_graph(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Parse a PDF CV and extract structured profile data using LangGraph."""
    if not file.filename or not validate_file_type(file.filename, ["pdf"]):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    repo = CandidateRepository(db)
    candidate = repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    raw_content = await file.read()
    if not raw_content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

    temp_file_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(raw_content)
            temp_file_path = temp_file.name

        graph_result = cv_profile_graph.invoke(
            {
                "raw_pdf_path": temp_file_path,
                "extracted_text": "",
                "structured_data": {},
                "error": None,
            }
        )

        if graph_result.get("error"):
            raise HTTPException(status_code=400, detail=graph_result["error"])

        structured_data = graph_result.get("structured_data", {})
        extracted_text = graph_result.get("extracted_text", "")

        clean_cv_text = sanitize_text(extracted_text)
        skills = [sanitize_text(skill) for skill in structured_data.get("skills", []) if skill]
        experience_years = int(structured_data.get("experience_years", 0) or 0)

        repo.update_profile(
            candidate_id=candidate_id,
            skills=skills,
            experience_years=experience_years,
            cv_text=clean_cv_text,
        )

        return CVGraphAnalysisResponse(
            candidate_id=candidate_id,
            extracted_text_length=len(clean_cv_text),
            structured_data=structured_data,
            error=None,
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

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

        # Keep the dashboard populated with realistic and profile-aware opportunities.
        _sync_generated_market_vacancies(
            db=db,
            candidate_id=existing.id,
            cv_text=clean_cv,
            profile_data=profile,
            preferred_location=clean_location,
        )
        
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

        # Keep the dashboard populated with realistic and profile-aware opportunities.
        _sync_generated_market_vacancies(
            db=db,
            candidate_id=candidate.id,
            cv_text=clean_cv,
            profile_data=profile,
            preferred_location=clean_location,
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
