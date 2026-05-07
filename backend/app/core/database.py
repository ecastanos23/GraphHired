# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Conexion sincronica a base de datos. Partes: engine SQLAlchemy, SessionLocal, dependencia get_db, inicializacion de tablas y migraciones ligeras.

"""
Database Connection and Session Management
SQLAlchemy setup - SQLite for dev, PostgreSQL for production
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configure engine
db_url = settings.get_database_url()
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from app.models.entities import Log, User, Candidate, Vacancy, Application, Appointment, AgentEvent
    Base.metadata.create_all(bind=engine)

    # Lightweight migration support for the class project. Existing Docker volumes
    # do not rerun init.sql, so additive columns must be created at app startup.
    with engine.begin() as connection:
        if db_url.startswith("postgresql"):
            connection.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS evidence JSONB DEFAULT '{}'::jsonb"))
            connection.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS next_steps JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS agent_reason TEXT"))
            # Comentario: Agregar columnas de snapshot para guardar perfil del candidato en el momento de la aplicación
            connection.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS snapshot_skills JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS snapshot_experience_years INTEGER DEFAULT 0"))
            # Ensure agent_events.metadata exists (JSONB) for model mapping
            connection.execute(text("ALTER TABLE agent_events ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb"))
            # Ensure candidates extended profile columns exist
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS education JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS experience JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS languages JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS summary TEXT"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS profile_gaps JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS recommended_roles JSONB DEFAULT '[]'::jsonb"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS cv_filename TEXT"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS parsed_at TIMESTAMP"))
            connection.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS analysis_model TEXT"))
        elif db_url.startswith("sqlite"):
            columns = {
                row[1]
                for row in connection.execute(text("PRAGMA table_info(applications)"))
                .fetchall()
            }
            if "evidence" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN evidence JSON DEFAULT '{}'"))
            if "next_steps" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN next_steps JSON DEFAULT '[]'"))
            if "agent_reason" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN agent_reason TEXT"))
            # Comentario: Agregar columnas de snapshot para guardar perfil del candidato al momento de aplicación
            if "snapshot_skills" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN snapshot_skills JSON DEFAULT '[]'"))
            if "snapshot_experience_years" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN snapshot_experience_years INTEGER DEFAULT 0"))
            # For SQLite, add metadata column if missing
            agent_cols = {row[1] for row in connection.execute(text("PRAGMA table_info(agent_events)")).fetchall()}
            if "metadata" not in agent_cols:
                connection.execute(text("ALTER TABLE agent_events ADD COLUMN metadata JSON DEFAULT '{}'"))
            # Ensure candidates extended profile columns exist for SQLite
            cand_cols = {row[1] for row in connection.execute(text("PRAGMA table_info(candidates)")) .fetchall()}
            if "education" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN education JSON DEFAULT '[]'"))
            if "experience" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN experience JSON DEFAULT '[]'"))
            if "languages" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN languages JSON DEFAULT '[]'"))
            if "certifications" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN certifications JSON DEFAULT '[]'"))
            if "summary" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN summary TEXT"))
            if "profile_gaps" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN profile_gaps JSON DEFAULT '[]'"))
            if "recommended_roles" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN recommended_roles JSON DEFAULT '[]'"))
            if "cv_filename" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN cv_filename TEXT"))
            if "parsed_at" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN parsed_at DATETIME"))
            if "analysis_model" not in cand_cols:
                connection.execute(text("ALTER TABLE candidates ADD COLUMN analysis_model TEXT"))
