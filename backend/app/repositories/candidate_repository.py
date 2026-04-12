"""
Candidate Repository
Data access layer for candidates
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.entities import Candidate
from app.models.schemas import CandidateCreate, CandidateUpdate

class CandidateRepository:
    """Repository for Candidate operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: CandidateCreate) -> Candidate:
        """Create a new candidate"""
        candidate = Candidate(**data.model_dump())
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
    
    def get_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """Get candidate by ID"""
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    def get_by_email(self, email: str) -> Optional[Candidate]:
        """Get candidate by email"""
        return self.db.query(Candidate).filter(Candidate.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Candidate]:
        """Get all candidates with pagination"""
        return self.db.query(Candidate).offset(skip).limit(limit).all()
    
    def update(self, candidate_id: int, data: CandidateUpdate) -> Optional[Candidate]:
        """Update candidate"""
        candidate = self.get_by_id(candidate_id)
        if not candidate:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)
        
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
    
    def update_profile(self, candidate_id: int, skills: List[str], experience_years: int, cv_text: str = None, embedding: List[float] = None) -> Optional[Candidate]:
        """Update candidate profile after AI analysis"""
        candidate = self.get_by_id(candidate_id)
        if not candidate:
            return None
        
        candidate.skills = skills
        candidate.experience_years = experience_years
        if cv_text:
            candidate.cv_text = cv_text
        if embedding:
            candidate.cv_embedding = embedding
        
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def update_cv_embedding(self, candidate_id: int, embedding: List[float]) -> bool:
        """Update only cv_embedding for a candidate."""
        candidate = self.get_by_id(candidate_id)
        if not candidate:
            return False

        candidate.cv_embedding = embedding
        self.db.commit()
        return True
    
    def delete(self, candidate_id: int) -> bool:
        """Delete candidate"""
        candidate = self.get_by_id(candidate_id)
        if not candidate:
            return False
        
        self.db.delete(candidate)
        self.db.commit()
        return True
    
    def search(self, query: str) -> List[Candidate]:
        """Search candidates by name or email"""
        search_pattern = f"%{query}%"
        return self.db.query(Candidate).filter(
            or_(
                Candidate.full_name.ilike(search_pattern),
                Candidate.email.ilike(search_pattern)
            )
        ).all()
