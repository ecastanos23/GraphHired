# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Repositorio de vacantes. Partes: crear, listar activas, actualizar embedding, buscar por criterios, desactivar y eliminar.

"""
Vacancy Repository
Data access layer for job vacancies
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from decimal import Decimal
from app.models.entities import Vacancy
from app.models.schemas import VacancyCreate

class VacancyRepository:
    """Repository for Vacancy operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: VacancyCreate) -> Vacancy:
        """Create a new vacancy"""
        vacancy = Vacancy(**data.model_dump())
        self.db.add(vacancy)
        self.db.commit()
        self.db.refresh(vacancy)
        return vacancy
    
    def get_by_id(self, vacancy_id: int) -> Optional[Vacancy]:
        """Get vacancy by ID"""
        return self.db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Vacancy]:
        """Get all vacancies with pagination"""
        query = self.db.query(Vacancy)
        if active_only:
            query = query.filter(Vacancy.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def update_embedding(self, vacancy_id: int, embedding: List[float]) -> Optional[Vacancy]:
        """Update vacancy embedding"""
        vacancy = self.get_by_id(vacancy_id)
        if not vacancy:
            return None
        
        vacancy.description_embedding = embedding
        self.db.commit()
        self.db.refresh(vacancy)
        return vacancy
    
    def search_by_criteria(
        self,
        work_modality: Optional[str] = None,
        min_salary: Optional[Decimal] = None,
        max_experience: Optional[int] = None,
        location: Optional[str] = None
    ) -> List[Vacancy]:
        """Search vacancies by criteria"""
        query = self.db.query(Vacancy).filter(Vacancy.is_active == True)
        
        if work_modality:
            query = query.filter(Vacancy.work_modality == work_modality)
        
        if min_salary:
            query = query.filter(
                or_(
                    Vacancy.salary_max >= min_salary,
                    Vacancy.salary_max.is_(None)
                )
            )
        
        if max_experience is not None:
            query = query.filter(Vacancy.experience_required <= max_experience)
        
        if location:
            query = query.filter(Vacancy.location.ilike(f"%{location}%"))
        
        return query.all()
    
    def deactivate(self, vacancy_id: int) -> bool:
        """Deactivate vacancy"""
        vacancy = self.get_by_id(vacancy_id)
        if not vacancy:
            return False
        
        vacancy.is_active = False
        self.db.commit()
        return True
    
    def delete(self, vacancy_id: int) -> bool:
        """Delete vacancy"""
        vacancy = self.get_by_id(vacancy_id)
        if not vacancy:
            return False
        
        self.db.delete(vacancy)
        self.db.commit()
        return True
