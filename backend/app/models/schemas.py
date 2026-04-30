"""
Pydantic Schemas for API Request/Response
Data validation and serialization
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

# =============================================================================
# Log Schemas (PoC)
# =============================================================================

class LogCreate(BaseModel):
    """Schema for creating a log entry"""
    input_text: str = Field(..., min_length=1, max_length=10000)

class LogResponse(BaseModel):
    """Schema for log response"""
    id: int
    input_text: str
    output_text: str
    created_at: datetime

    class Config:
        from_attributes = True

# =============================================================================
# Candidate Schemas
# =============================================================================

class CandidateCreate(BaseModel):
    """Schema for candidate registration"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    cv_text: Optional[str] = None
    expected_salary: Optional[Decimal] = Field(None, ge=0)
    work_modality: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    location: Optional[str] = Field(None, max_length=255)

    @validator('full_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full name is required')
        return v.strip()

class CandidateUpdate(BaseModel):
    """Schema for updating candidate"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    cv_text: Optional[str] = None
    expected_salary: Optional[Decimal] = Field(None, ge=0)
    work_modality: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    location: Optional[str] = Field(None, max_length=255)

class CandidateResponse(BaseModel):
    """Schema for candidate response"""
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    expected_salary: Optional[Decimal]
    work_modality: Optional[str]
    location: Optional[str]
    skills: List[str] = []
    experience_years: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Auth Schemas
# =============================================================================

class RegisterRequest(BaseModel):
    """Schema for registering a candidate user."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    cv_text: Optional[str] = None
    expected_salary: Optional[Decimal] = Field(None, ge=0)
    work_modality: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    location: Optional[str] = Field(None, max_length=255)


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class AuthUser(BaseModel):
    id: int
    email: str
    candidate_id: Optional[int]
    candidate: Optional[CandidateResponse] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class CVUpload(BaseModel):
    """Schema for CV upload with expectations"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    cv_text: str = Field(..., min_length=10)
    expected_salary: Decimal = Field(..., ge=0)
    work_modality: str = Field(..., pattern="^(remote|hybrid|onsite)$")
    location: str = Field(..., min_length=2, max_length=255)


class ParsedCVResponse(BaseModel):
    """Profile fields extracted from an uploaded CV PDF."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    education: Optional[str] = None
    summary: str = ""
    profile_gaps: List[str] = []
    recommended_roles: List[str] = []
    cv_text: str
    extracted_text_length: int

# =============================================================================
# Vacancy Schemas
# =============================================================================

class VacancyCreate(BaseModel):
    """Schema for creating a vacancy"""
    title: str = Field(..., min_length=2, max_length=255)
    company: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)
    work_modality: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    location: Optional[str] = Field(None, max_length=255)
    experience_required: int = Field(default=0, ge=0)

class VacancyResponse(BaseModel):
    """Schema for vacancy response"""
    id: int
    title: str
    company: str
    description: str
    required_skills: List[str]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    work_modality: Optional[str]
    location: Optional[str]
    experience_required: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# =============================================================================
# Matching Schemas
# =============================================================================

class MatchResult(BaseModel):
    """Schema for a single match result"""
    vacancy_id: int
    title: str
    company: str
    match_score: float = Field(..., ge=0, le=100)
    salary_range: str
    work_modality: Optional[str]
    location: Optional[str]
    matching_skills: List[str]
    missing_skills: List[str]
    score_breakdown: dict[str, float] = {}
    match_explanation: str = ""

class MatchingResponse(BaseModel):
    """Schema for matching response"""
    candidate_id: int
    candidate_name: str
    total_matches: int
    matches: List[MatchResult]

# =============================================================================
# Application Schemas
# =============================================================================

class ApplicationCreate(BaseModel):
    """Schema for creating an application"""
    candidate_id: int
    vacancy_id: int

class ApplicationResponse(BaseModel):
    """Schema for application response"""
    id: int
    candidate_id: int
    vacancy_id: int
    match_score: Optional[Decimal]
    status: str
    evidence: Optional[dict[str, Any]] = None
    next_steps: List[str] = []
    agent_reason: Optional[str] = None
    applied_at: datetime
    vacancy_title: Optional[str] = None
    company: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    """Create a candidate interview/follow-up appointment."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    start_at: datetime
    end_at: datetime


class AppointmentResponse(BaseModel):
    id: int
    application_id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    start_at: datetime
    end_at: datetime
    google_calendar_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgentEventResponse(BaseModel):
    id: int
    candidate_id: Optional[int]
    application_id: Optional[int]
    agent_name: str
    action: str
    reason: str
    input_summary: Optional[str]
    output_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# =============================================================================
# Profile Analysis Schemas
# =============================================================================

class ProfileAnalysis(BaseModel):
    """Schema for AI-extracted profile data"""
    skills: List[str]
    experience_years: int
    education: Optional[str]
    summary: str
    strengths: List[str]
    recommended_roles: List[str]


# =============================================================================
# Semantic Matching Schemas
# =============================================================================

class SemanticMatchItem(BaseModel):
    """Single semantic match item"""
    vacancy_id: int
    title: str
    company: str
    similarity_score: float = Field(..., ge=0, le=100)
    work_modality: Optional[str]
    location: Optional[str]


class SemanticMatchingResponse(BaseModel):
    """Semantic matching response using pgvector cosine distance"""
    candidate_id: int
    total_matches: int
    matches: List[SemanticMatchItem]
    status: str = "success"
    engine: Optional[str] = None


class CVGraphAnalysisResponse(BaseModel):
    """Response for CV PDF parsing workflow"""
    candidate_id: int
    extracted_text_length: int
    structured_data: dict
    error: Optional[str] = None
