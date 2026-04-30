"""Vacancy Agent - curates and normalizes demo vacancies for a candidate."""
from decimal import Decimal
import re

from sqlalchemy.orm import Session

from app.agents.profile_agent import generate_colombia_job_dataset
from app.models.entities import Vacancy
from app.models.schemas import VacancyCreate
from app.repositories.agent_event_repository import AgentEventRepository
from app.repositories.vacancy_repository import VacancyRepository


AUTO_DATASET_MARKER = "[AUTO_DATASET_CANDIDATE:"


def _salary_string_to_decimals(salary_range: str) -> tuple[Decimal, Decimal]:
    values = re.findall(r"\d[\d\.]*", salary_range or "")
    parsed: list[Decimal] = []
    for value in values[:2]:
        clean = value.replace(".", "")
        if clean.isdigit():
            parsed.append(Decimal(clean))

    if len(parsed) == 2:
        low, high = sorted(parsed)
        return low, high
    if len(parsed) == 1:
        return parsed[0], parsed[0]
    return Decimal("3000000"), Decimal("5000000")


def _mode_to_db(mode: str) -> str:
    normalized = (mode or "").strip().lower()
    if normalized == "remoto":
        return "remote"
    if normalized in {"hibrido", "hibrido", "hybrid"}:
        return "hybrid"
    return "onsite"


def _experience_from_title(title: str) -> int:
    title_lower = (title or "").lower()
    if "junior" in title_lower or "auxiliar" in title_lower:
        return 1
    if "senior" in title_lower or "lider" in title_lower or "lead" in title_lower:
        return 5
    if "gerente" in title_lower or "director" in title_lower:
        return 8
    return 3


def sync_curated_market_vacancies(
    db: Session,
    candidate_id: int,
    cv_text: str,
    profile_data: dict,
    preferred_location: str,
) -> int:
    """Create a fresh 20-item Colombia market dataset tied to one candidate."""
    marker = f"{AUTO_DATASET_MARKER}{candidate_id}]"

    db.query(Vacancy).filter(Vacancy.description.contains(marker)).delete(synchronize_session=False)

    dataset = generate_colombia_job_dataset(
        cv_text=cv_text,
        profile_data=profile_data,
        preferred_location=preferred_location,
    )

    vacancy_repo = VacancyRepository(db)
    created_count = 0
    for item in dataset[:20]:
        salary_min, salary_max = _salary_string_to_decimals(str(item.get("salary", "")))
        skills_owned = [str(skill).strip() for skill in item.get("skills_owned", []) if str(skill).strip()]
        skills_gap = [str(skill).strip() for skill in item.get("skills_to_develop", []) if str(skill).strip()]
        required_skills = list(dict.fromkeys((skills_owned + skills_gap)))

        vacancy_data = VacancyCreate(
            title=str(item.get("title", "Cargo no especificado")),
            company=str(item.get("company", "Empresa Colombia")),
            description=(
                f"{marker} Oferta sugerida por perfil CV. "
                f"Match estimado: {item.get('match_percentage', 55)}%. "
                f"Habilidades actuales: {', '.join(skills_owned)}. "
                f"Habilidades por fortalecer: {', '.join(skills_gap)}."
            ),
            required_skills=required_skills,
            salary_min=salary_min,
            salary_max=salary_max,
            work_modality=_mode_to_db(str(item.get("mode", "Presencial"))),
            location=str(item.get("location", preferred_location or "Bogota")),
            experience_required=_experience_from_title(str(item.get("title", ""))),
        )
        vacancy_repo.create(vacancy_data)
        created_count += 1

    AgentEventRepository(db).create(
        candidate_id=candidate_id,
        agent_name="Agente de Vacantes",
        action="Normalizo dataset curado",
        reason="Se genero un conjunto reproducible de vacantes Colombia ajustado al perfil y ubicacion del candidato.",
        input_summary=f"skills={profile_data.get('skills', [])[:6]}, location={preferred_location}",
        output_summary=f"{created_count} vacantes activas para el candidato",
    )
    return created_count
