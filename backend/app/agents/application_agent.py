# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Agente auxiliar de postulacion y explicacion. Partes: desglose de score, explicacion de match, evidencia de postulacion, proximos pasos y razon del agente.

"""Application and explanation agents for the final demo."""
from __future__ import annotations

from decimal import Decimal

from app.models.entities import Candidate, Vacancy


def build_score_breakdown(result: dict) -> dict[str, float]:
    """Expose LangGraph scoring nodes as a UI-friendly breakdown."""
    return {
        "skills": float(result.get("skill_score", 0.0)),
        "experience": float(result.get("experience_score", 0.0)),
        "salary": float(result.get("salary_score", 0.0)),
        "modality": float(result.get("modality_score", 0.0)),
    }


def build_match_explanation(candidate: Candidate, vacancy: Vacancy, result: dict) -> str:
    """Explain why a vacancy was recommended to the candidate."""
    matching_skills = result.get("matching_skills", []) or []
    missing_skills = result.get("missing_skills", []) or []
    score = float(result.get("total_score", 0.0))

    reasons: list[str] = []
    if matching_skills:
        reasons.append(f"coincide en {', '.join(matching_skills[:4])}")
    if vacancy.work_modality and candidate.work_modality == vacancy.work_modality:
        reasons.append(f"respeta la modalidad {vacancy.work_modality}")
    if vacancy.location and candidate.location:
        reasons.append(f"esta alineada con la ubicacion {vacancy.location}")
    if candidate.expected_salary and vacancy.salary_max and Decimal(candidate.expected_salary) <= vacancy.salary_max:
        reasons.append("esta dentro de la aspiracion salarial")

    if not reasons:
        reasons.append("mantiene una afinidad general con el perfil")

    gap_text = ""
    if missing_skills:
        gap_text = f" Para subir el match, conviene fortalecer {', '.join(missing_skills[:3])}."

    return (
        f"La IA recomienda {vacancy.company} para el rol {vacancy.title} con {score:.1f}% "
        f"porque {', '.join(reasons)}.{gap_text}"
    )


def build_application_evidence(candidate: Candidate, vacancy: Vacancy, result: dict) -> dict:
    """Build auditable evidence for a simulated application."""
    return {
        "candidate": candidate.full_name,
        "candidate_email": candidate.email,
        "company": vacancy.company,
        "vacancy": vacancy.title,
        "match_score": float(result.get("total_score", 0.0)),
        "matching_skills": result.get("matching_skills", []),
        "missing_skills": result.get("missing_skills", []),
        "decision": "Postulacion simulada enviada desde GraphHired",
    }


def build_followup_steps(vacancy: Vacancy) -> list[str]:
    """Generate next steps for the follow-up agent."""
    return [
        f"Revisar respuesta de {vacancy.company} en 48 horas.",
        "Preparar respuestas sobre experiencia, habilidades clave y motivacion.",
        "Agendar entrevista si el estado cambia a entrevista.",
    ]


def build_application_reason(vacancy: Vacancy, result: dict) -> str:
    """Short reason shown in the process board."""
    score = float(result.get("total_score", 0.0))
    matching = result.get("matching_skills", []) or []
    if matching:
        return f"Postulacion sugerida por {score:.1f}% de match y coincidencia en {', '.join(matching[:3])}."
    return f"Postulacion sugerida por {score:.1f}% de match general con {vacancy.company}."
