"""
Application Repository
Data access layer for job applications
"""
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from decimal import Decimal
from app.models.entities import Application, Vacancy

class ApplicationRepository:
    """Repository for Application operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, candidate_id: int, vacancy_id: int, match_score: Decimal = None) -> Application:
        """Create a new application"""
        application = Application(
            candidate_id=candidate_id,
            vacancy_id=vacancy_id,
            match_score=match_score,
            status="pending"
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def get_by_id(self, application_id: int) -> Optional[Application]:
        """Get application by ID with relationships"""
        return self.db.query(Application)\
            .options(joinedload(Application.candidate), joinedload(Application.vacancy))\
            .filter(Application.id == application_id).first()
    
    def get_by_candidate(self, candidate_id: int) -> List[Application]:
        """Get all applications for a candidate"""
        return self.db.query(Application)\
            .options(joinedload(Application.vacancy))\
            .filter(Application.candidate_id == candidate_id)\
            .order_by(Application.applied_at.desc()).all()
    
    def get_by_vacancy(self, vacancy_id: int) -> List[Application]:
        """Get all applications for a vacancy"""
        return self.db.query(Application)\
            .options(joinedload(Application.candidate))\
            .filter(Application.vacancy_id == vacancy_id)\
            .order_by(Application.match_score.desc()).all()
    
    def exists(self, candidate_id: int, vacancy_id: int) -> bool:
        """Check if application already exists"""
        return self.db.query(Application).filter(
            Application.candidate_id == candidate_id,
            Application.vacancy_id == vacancy_id
        ).first() is not None
    
    def update_status(self, application_id: int, status: str) -> Optional[Application]:
        """Update application status"""
        application = self.db.query(Application).filter(Application.id == application_id).first()
        if not application:
            return None
        
        application.status = status
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def delete(self, application_id: int) -> bool:
        """Delete application"""
        application = self.db.query(Application).filter(Application.id == application_id).first()
        if not application:
            return False
        
        self.db.delete(application)
        self.db.commit()
        return True
