"""
Log Repository
Data access layer for logs
"""
from sqlalchemy.orm import Session
from app.models.entities import Log

class LogRepository:
    """Repository for Log operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, input_text: str, output_text: str) -> Log:
        """Create a new log entry"""
        log = Log(input_text=input_text, output_text=output_text)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_all(self, limit: int = 100) -> list[Log]:
        """Get all logs"""
        return self.db.query(Log).order_by(Log.created_at.desc()).limit(limit).all()
    
    def get_by_id(self, log_id: int) -> Log | None:
        """Get log by ID"""
        return self.db.query(Log).filter(Log.id == log_id).first()
