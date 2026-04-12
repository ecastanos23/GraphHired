"""
Database Connection and Session Management
SQLAlchemy setup - SQLite for dev, PostgreSQL for production
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configure engine
db_url = settings.get_database_url()
engine = create_engine(db_url)

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
    from app.models.entities import Log, Candidate, Vacancy, Application
    Base.metadata.create_all(bind=engine)
