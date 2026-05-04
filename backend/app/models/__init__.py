# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Inicializa el paquete de modelos ORM y schemas Pydantic.

"""Models module initialization"""
from app.models.entities import Log, Candidate, Vacancy, Application
from app.models.schemas import (
    LogCreate, LogResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse, CVUpload,
    VacancyCreate, VacancyResponse,
    MatchResult, MatchingResponse,
    ApplicationCreate, ApplicationResponse,
    ProfileAnalysis
)
