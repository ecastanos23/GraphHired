# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Rutas de citas. Partes: creacion/listado de appointments, validacion de fechas, link Google Calendar y evento de trazabilidad.

"""Application process endpoints: appointments and follow-up."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.agents.followup_agent import build_google_calendar_url, default_appointment_payload
from app.core.database import get_db
from app.core.security import sanitize_text
from app.models.schemas import AppointmentCreate, AppointmentResponse
from app.repositories.agent_event_repository import AgentEventRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.appointment_repository import AppointmentRepository

router = APIRouter()


@router.post("/{application_id}/appointments", response_model=AppointmentResponse)
async def create_appointment(
    application_id: int,
    data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    """Schedule an interview/follow-up and return a Google Calendar link."""
    application = ApplicationRepository(db).get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if data.end_at <= data.start_at:
        raise HTTPException(status_code=400, detail="end_at must be after start_at")

    defaults = default_appointment_payload(application)
    title = sanitize_text(data.title or defaults["title"])
    description = sanitize_text(data.description or defaults["description"])
    location = sanitize_text(data.location or defaults["location"])
    calendar_url = build_google_calendar_url(
        title=title,
        start_at=data.start_at,
        end_at=data.end_at,
        details=description,
        location=location,
    )

    appointment = AppointmentRepository(db).create(
        application_id=application_id,
        title=title,
        description=description,
        location=location,
        start_at=data.start_at,
        end_at=data.end_at,
        google_calendar_url=calendar_url,
    )
    application.status = "entrevista"
    db.commit()

    AgentEventRepository(db).create(
        candidate_id=application.candidate_id,
        application_id=application.id,
        agent_name="Agente de Seguimiento",
        action="Agendo cita y genero enlace Calendar",
        reason="La postulacion avanzo a entrevista y se preparo un evento prellenado sin OAuth.",
        input_summary=f"application_id={application.id}, start_at={data.start_at.isoformat()}",
        output_summary=f"calendar_url={calendar_url[:120]}",
    )
    return appointment


@router.get("/{application_id}/appointments", response_model=List[AppointmentResponse])
async def get_appointments(application_id: int, db: Session = Depends(get_db)):
    """List appointments for an application."""
    application = ApplicationRepository(db).get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return AppointmentRepository(db).get_by_application(application_id)
