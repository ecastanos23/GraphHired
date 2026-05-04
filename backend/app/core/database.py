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
        elif db_url.startswith("sqlite"):
            columns = {
                row[1]
                for row in connection.execute(text("PRAGMA table_info(applications)")).fetchall()
            }
            if "evidence" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN evidence JSON DEFAULT '{}'"))
            if "next_steps" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN next_steps JSON DEFAULT '[]'"))
            if "agent_reason" not in columns:
                connection.execute(text("ALTER TABLE applications ADD COLUMN agent_reason TEXT"))
