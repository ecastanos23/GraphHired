# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Rutas de autenticacion. Partes: registro con candidato asociado, login, /me, token JWT, generacion de embedding y eventos de agente.

"""Authentication routes for candidate users."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.profile_agent import analyze_profile
from app.agents.vacancy_agent import sync_curated_market_vacancies
from app.core.database import SessionLocal, get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    sanitize_email,
    sanitize_text,
    verify_password,
)
from app.models.entities import User
from app.models.schemas import AuthUser, CandidateCreate, CandidateResponse, LoginRequest, RegisterRequest, TokenResponse
from app.repositories.agent_event_repository import AgentEventRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.user_repository import UserRepository
from app.services.embedding_service import EmbeddingService

router = APIRouter()


def _generate_and_store_candidate_embedding(candidate_id: int, cv_text: str | None) -> None:
    embedding = EmbeddingService.generate_embedding(cv_text or "")
    if embedding is None:
        return

    db = SessionLocal()
    try:
        CandidateRepository(db).update_cv_embedding(candidate_id=candidate_id, embedding=embedding)
    finally:
        db.close()


def _build_token_response(user: User) -> TokenResponse:
    candidate_response = CandidateResponse.model_validate(user.candidate) if user.candidate else None
    auth_user = AuthUser(
        id=user.id,
        email=user.email,
        candidate_id=user.candidate_id,
        candidate=candidate_response,
    )
    return TokenResponse(
        access_token=create_access_token(user.email),
        token_type="bearer",
        user=auth_user,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Register a candidate user and create the associated candidate profile."""
    clean_email = sanitize_email(str(data.email))
    user_repo = UserRepository(db)
    if user_repo.get_by_email(clean_email):
        raise HTTPException(status_code=400, detail="Email already registered")

    candidate_repo = CandidateRepository(db)
    existing_candidate = candidate_repo.get_by_email(clean_email)
    if existing_candidate:
        candidate = existing_candidate
        candidate.full_name = sanitize_text(data.full_name)
        candidate.phone = sanitize_text(data.phone or "")
        candidate.expected_salary = data.expected_salary
        candidate.work_modality = data.work_modality
        candidate.location = sanitize_text(data.location or "")
        if data.cv_text:
            candidate.cv_text = sanitize_text(data.cv_text)
        db.commit()
        db.refresh(candidate)
    else:
        candidate_data = CandidateCreate(
            email=clean_email,
            full_name=sanitize_text(data.full_name),
            phone=sanitize_text(data.phone or "") or None,
            cv_text=sanitize_text(data.cv_text or "") or None,
            expected_salary=data.expected_salary,
            work_modality=data.work_modality,
            location=sanitize_text(data.location or "") or None,
        )
        candidate = candidate_repo.create(candidate_data)

    if candidate.cv_text:
        profile = analyze_profile(
            candidate.cv_text,
            {
                "salary": candidate.expected_salary,
                "modality": candidate.work_modality,
                "location": candidate.location,
            },
        )
        candidate_repo.update_profile(
            candidate.id,
            skills=profile["skills"],
            experience_years=profile["experience_years"],
        )
        sync_curated_market_vacancies(
            db=db,
            candidate_id=candidate.id,
            cv_text=candidate.cv_text,
            profile_data=profile,
            preferred_location=candidate.location or "Bogota",
        )
        background_tasks.add_task(_generate_and_store_candidate_embedding, candidate.id, candidate.cv_text)

    user = user_repo.create(
        email=clean_email,
        hashed_password=hash_password(data.password),
        candidate_id=candidate.id,
    )
    user = user_repo.get_by_id(user.id) or user
    AgentEventRepository(db).create(
        candidate_id=candidate.id,
        agent_name="Agente de Perfil",
        action="Creo cuenta y perfil candidato",
        reason="El candidato completo el registro y quedo listo para recibir recomendaciones.",
        input_summary=f"email={clean_email}, location={candidate.location}",
        output_summary=f"candidate_id={candidate.id}",
    )
    return _build_token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a candidate user."""
    clean_email = sanitize_email(str(data.email))
    user = UserRepository(db).get_by_email(clean_email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _build_token_response(user)


@router.get("/me", response_model=AuthUser)
async def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user."""
    candidate_response = CandidateResponse.model_validate(current_user.candidate) if current_user.candidate else None
    return AuthUser(
        id=current_user.id,
        email=current_user.email,
        candidate_id=current_user.candidate_id,
        candidate=candidate_response,
    )
