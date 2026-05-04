# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Agente de seguimiento. Partes: conversion de fechas UTC, construccion del link Google Calendar sin OAuth y valores por defecto de entrevista.

"""Follow-up Agent - appointments and Google Calendar links."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

from app.models.entities import Application


def _calendar_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_google_calendar_url(
    title: str,
    start_at: datetime,
    end_at: datetime,
    details: str,
    location: str | None,
) -> str:
    """Build a Google Calendar template link without OAuth."""
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{_calendar_timestamp(start_at)}/{_calendar_timestamp(end_at)}",
        "details": details,
        "location": location or "Google Meet",
    }
    return f"https://calendar.google.com/calendar/render?{urlencode(params)}"


def default_appointment_payload(application: Application) -> dict:
    company = application.vacancy.company if application.vacancy else "empresa"
    vacancy = application.vacancy.title if application.vacancy else "vacante"
    title = f"Entrevista con {company}"
    description = (
        f"Entrevista sugerida desde GraphHired para la vacante {vacancy}. "
        "Revisar evidencia de postulacion y preparar respuestas antes de la reunion."
    )
    location = "Google Meet"
    return {"title": title, "description": description, "location": location}
