"""Repository for application appointments."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.entities import Appointment


class AppointmentRepository:
    """Data access layer for interview appointments."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        application_id: int,
        title: str,
        description: str | None,
        location: str | None,
        start_at,
        end_at,
        google_calendar_url: str,
    ) -> Appointment:
        appointment = Appointment(
            application_id=application_id,
            title=title,
            description=description,
            location=location,
            start_at=start_at,
            end_at=end_at,
            google_calendar_url=google_calendar_url,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_by_application(self, application_id: int) -> List[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(Appointment.application_id == application_id)
            .order_by(Appointment.start_at.asc())
            .all()
        )

    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
