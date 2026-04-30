"""
SQLAlchemy Database Models
ORM models - Text for embeddings (SQLite), Vector for production (PostgreSQL+pgvector)
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings

# Use Text for SQLite, Vector for PostgreSQL
if settings.USE_SQLITE:
    EmbeddingColumn = Text
else:
    from pgvector.sqlalchemy import Vector
    EmbeddingColumn = Vector(1536)

class Log(Base):
    """Log model for PoC testing"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    """Application user for candidate login."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    candidate = relationship("Candidate", back_populates="user")


class Candidate(Base):
    """Candidate/Job seeker model"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    cv_text = Column(Text, nullable=True)
    cv_embedding = Column(EmbeddingColumn, nullable=True)
    expected_salary = Column(DECIMAL(12, 2), nullable=True)
    work_modality = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="candidate", uselist=False)
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")


class Vacancy(Base):
    """Job vacancy model"""
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    description_embedding = Column(EmbeddingColumn, nullable=True)
    required_skills = Column(JSON, default=list)
    salary_min = Column(DECIMAL(12, 2), nullable=True)
    salary_max = Column(DECIMAL(12, 2), nullable=True)
    work_modality = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    experience_required = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    applications = relationship("Application", back_populates="vacancy", cascade="all, delete-orphan")


class Application(Base):
    """Job application model"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(DECIMAL(5, 2), nullable=True)
    status = Column(String(50), default="postulado")
    evidence = Column(JSON, default=dict)
    next_steps = Column(JSON, default=list)
    agent_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")
    appointments = relationship("Appointment", back_populates="application", cascade="all, delete-orphan")


class Appointment(Base):
    """Interview or follow-up appointment linked to an application."""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    google_calendar_url = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    application = relationship("Application", back_populates="appointments")


class AgentEvent(Base):
    """Trace event for agentic decisions and workflow steps."""
    __tablename__ = "agent_events"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
