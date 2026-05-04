# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Agente de perfil. Partes: prompts de extraccion, analisis de CV, fallback basico, normalizacion de datos y generacion de dataset Colombia.

"""
Profile Agent - LangGraph agent for CV analysis and profile extraction
Uses LLM to extract skills, experience, and generate recommendations
"""
from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re
import unicodedata

from app.core.config import settings

class ProfileState(TypedDict):
    """
    State for profile analysis (5.2 Proceso)
    Includes CV text and candidate expectations for semantic matching
    """
    cv_text: str
    expectations: dict  # {salary, modality, location}
    extracted_data: dict  # Output from AI extraction
    # Extended fields for full analysis
    skills: List[str]
    experience_years: int
    education: Optional[str]
    summary: str
    strengths: List[str]
    recommended_roles: List[str]
    match_confidence: float
    error: Optional[str]

# Optimized prompt for token efficiency (environmental consideration)
EXTRACTION_PROMPT = """Analyze this CV and extract information in JSON format:
{
  "skills": ["skill1", "skill2"],
  "experience_years": number,
  "education": "highest degree",
  "summary": "2-sentence professional summary",
  "strengths": ["strength1", "strength2", "strength3"],
  "recommended_roles": ["role1", "role2", "role3"]
}

CV:
{cv_text}

Return ONLY valid JSON, no explanations."""

JOB_DATASET_PROMPT = """Actua como experto en reclutamiento y mercado laboral de Colombia.
Genera exactamente 20 ofertas de empleo reales o altamente realistas para Colombia (2026),
incluyendo variedad de seniority (junior, mid, senior, gerencial) y sectores:
Tecnologia, Finanzas, Marketing, Salud, Ingenieria Civil.

Contexto de candidato:
- Skills detectadas: {skills}
- Ubicacion preferida: {location}
- Experiencia aproximada (anios): {experience}

Entrega SOLO un arreglo JSON valido. Cada item debe tener estos campos exactos:
- title (string)
- company (string)
- match_percentage (number entre 40 y 95)
- salary (string en formato "$X.XXX.XXX - $Y.YYY.YYY")
- mode ("Remoto" | "Hibrido" | "Presencial")
- location ("Bogota" | "Medellin" | "Cali" | "Barranquilla" | "Bucaramanga")
- skills_owned (array de 3 strings)
- skills_to_develop (array de 1 o 2 strings)

Restricciones:
- Salarios coherentes con mercado colombiano 2026.
- Sin texto adicional fuera del JSON.
"""

def get_llm():
    """Get LLM instance with optimized settings"""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,  # Deterministic output for consistency
        max_tokens=500,  # Limit tokens for efficiency
        google_api_key=api_key
    )

def extract_profile_node(state: ProfileState) -> ProfileState:
    """
    Node that extracts profile information from CV using LLM (5.2 Proceso)
    Aquí es donde ocurre la "magia" de la IA
    Falls back to basic extraction if no API key available
    """
    cv_text = state["cv_text"]
    expectations = state.get("expectations", {})
    
    # Try LLM extraction first
    llm = get_llm()
    if llm:
        try:
            prompt = EXTRACTION_PROMPT.format(cv_text=cv_text[:3000])  # Limit input for token efficiency
            messages = [
                SystemMessage(content="You are a CV analyzer. Extract structured data from CVs."),
                HumanMessage(content=prompt)
            ]
            response = llm.invoke(messages)
            
            # Parse JSON response
            data = json.loads(response.content)
            
            # Build extracted_data with candidate name and AI analysis
            extracted_data = {
                "name": data.get("name", "Candidato"),
                "top_skills": data.get("skills", [])[:5],
                "match_confidence": 0.95,  # Initial confidence
                "analysis_method": "llm"
            }
            
            return {
                **state,
                "extracted_data": extracted_data,
                "skills": data.get("skills", []),
                "experience_years": data.get("experience_years", 0),
                "education": data.get("education"),
                "summary": data.get("summary", ""),
                "strengths": data.get("strengths", []),
                "recommended_roles": data.get("recommended_roles", []),
                "match_confidence": 0.95,
                "error": None
            }
        except Exception as e:
            # Fall through to basic extraction
            pass
    
    # Basic extraction fallback (no LLM) - Simulación de extracción semántica
    result = basic_extraction(state)
    
    # Build extracted_data for fallback case
    result["extracted_data"] = {
        "name": "Candidato",  # Name would be extracted from CV
        "top_skills": result["skills"][:5] if result["skills"] else ["Python", "SQL", "FastAPI"],
        "match_confidence": result.get("match_confidence", 0.75),
        "analysis_method": "basic"
    }
    
    return result

def basic_extraction(state: ProfileState) -> ProfileState:
    """
    Basic keyword-based extraction when LLM is unavailable
    Simulación de extracción semántica (5.2)
    """
    cv_text = state["cv_text"].lower()
    
    # Common tech skills to detect
    tech_skills = [
        "python", "javascript", "java", "react", "node.js", "sql", "docker",
        "kubernetes", "aws", "azure", "git", "typescript", "fastapi", "django",
        "flask", "mongodb", "postgresql", "redis", "graphql", "rest", "api",
        "machine learning", "ai", "data science", "devops", "ci/cd", "agile"
    ]
    
    found_skills = [skill for skill in tech_skills if skill in cv_text]
    
    # Estimate experience from keywords
    experience = 0
    if "senior" in cv_text or "5 años" in cv_text or "5 years" in cv_text:
        experience = 5
    elif "mid" in cv_text or "3 years" in cv_text or "4 years" in cv_text or "3 años" in cv_text:
        experience = 3
    elif "junior" in cv_text or "1 year" in cv_text or "2 years" in cv_text or "1 año" in cv_text:
        experience = 1
    
    # Calculate match confidence based on skills found
    match_confidence = min(0.95, 0.5 + (len(found_skills) * 0.05))
    
    return {
        **state,
        "extracted_data": {},  # Will be filled by caller
        "skills": found_skills[:10],  # Limit to top 10
        "experience_years": experience,
        "education": "Not detected",
        "summary": "Perfil analizado con extracción básica",
        "strengths": found_skills[:3] if found_skills else ["Resolución de problemas"],
        "recommended_roles": ["Software Developer"],
        "match_confidence": match_confidence,
        "error": None
    }

def create_profile_graph() -> StateGraph:
    """Create the profile analysis workflow"""
    workflow = StateGraph(ProfileState)
    
    workflow.add_node("extract", extract_profile_node)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", END)
    
    return workflow.compile()

# Singleton instance - El "Cerebro" compilado (5.2)
agent_executor = create_profile_graph()

def analyze_profile(cv_text: str, expectations: dict = None) -> dict:
    """
    Analyze CV and extract profile information (5.2 Proceso)
    Returns structured profile data including extracted_data
    
    Args:
        cv_text: Raw CV text content
        expectations: Optional dict with {salary, modality, location}
    
    Returns:
        Dictionary with extracted profile information
    """
    if expectations is None:
        expectations = {}
    
    initial_state: ProfileState = {
        "cv_text": cv_text,
        "expectations": expectations,
        "extracted_data": {},
        "skills": [],
        "experience_years": 0,
        "education": None,
        "summary": "",
        "strengths": [],
        "recommended_roles": [],
        "match_confidence": 0.0,
        "error": None
    }
    
    result = agent_executor.invoke(initial_state)
    
    return {
        "extracted_data": result["extracted_data"],
        "skills": result["skills"],
        "experience_years": result["experience_years"],
        "education": result["education"],
        "summary": result["summary"],
        "strengths": result["strengths"],
        "recommended_roles": result["recommended_roles"],
        "match_confidence": result["match_confidence"]
    }


def _clean_json_payload(raw_content: str) -> str:
    """Extract a JSON array payload from model output."""
    text = raw_content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    start_idx = text.find("[")
    end_idx = text.rfind("]")
    if start_idx >= 0 and end_idx > start_idx:
        return text[start_idx : end_idx + 1]
    return text


def _safe_float(value: Any, default: float = 50.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_mode(mode: str) -> str:
    mode_value = (mode or "").strip().lower()
    if mode_value in {"remoto", "remote"}:
        return "Remoto"
    if mode_value in {"hibrido", "híbrido", "hybrid"}:
        return "Hibrido"
    return "Presencial"


def _normalize_location(location: str) -> str:
    raw = (location or "").strip().lower()
    if not raw:
        return "Bogota"

    normalized = unicodedata.normalize("NFD", raw)
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    normalized = re.sub(r"[^a-z\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    aliases = {
        "Bogota": {"bogota", "bogota dc", "bogota d c", "bta"},
        "Medellin": {"medellin", "medallo", "med"},
        "Cali": {"cali", "santiago de cali"},
        "Barranquilla": {"barranquilla", "bquilla", "baq"},
        "Bucaramanga": {"bucaramanga", "bga"},
    }

    for canonical, values in aliases.items():
        for value in values:
            if normalized == value or value in normalized:
                return canonical

    return "Bogota"


def _score_from_overlap(candidate_skills: list[str], job_skills: list[str]) -> float:
    if not job_skills:
        return 50.0
    cset = {s.lower() for s in candidate_skills if s}
    jset = {s.lower() for s in job_skills if s}
    overlap = len(cset.intersection(jset))
    ratio = overlap / max(1, len(jset))
    score = 40.0 + (ratio * 55.0)
    return max(40.0, min(95.0, round(score, 1)))


def _fallback_market_dataset(candidate_skills: list[str], preferred_location: str) -> list[dict[str, Any]]:
    """Deterministic 20-item Colombia dataset (2026 salary ranges)."""
    templates = [
        {"title": "Desarrollador Frontend Junior", "company": "Rappi", "mode": "Hibrido", "location": "Bogota", "salary": "$4.000.000 - $6.000.000", "required": ["javascript", "react", "typescript"]},
        {"title": "Ingeniero Backend Python Mid", "company": "Mercado Libre Colombia", "mode": "Remoto", "location": "Medellin", "salary": "$7.500.000 - $11.000.000", "required": ["python", "fastapi", "sql"]},
        {"title": "Ingeniero de Datos Senior", "company": "Nubank", "mode": "Hibrido", "location": "Bogota", "salary": "$12.000.000 - $16.500.000", "required": ["python", "sql", "spark"]},
        {"title": "Gerente de Tecnologia", "company": "Bancolombia", "mode": "Presencial", "location": "Medellin", "salary": "$18.000.000 - $24.000.000", "required": ["arquitectura de software", "liderazgo", "cloud"]},
        {"title": "Analista Financiero Junior", "company": "Grupo Nutresa", "mode": "Hibrido", "location": "Medellin", "salary": "$3.800.000 - $5.300.000", "required": ["excel avanzado", "contabilidad", "sap"]},
        {"title": "Especialista de Planeacion Financiera", "company": "Davivienda", "mode": "Hibrido", "location": "Bogota", "salary": "$7.000.000 - $9.500.000", "required": ["modelacion financiera", "power bi", "sql"]},
        {"title": "Lider de Riesgo de Credito", "company": "BBVA Colombia", "mode": "Presencial", "location": "Bogota", "salary": "$11.000.000 - $14.500.000", "required": ["riesgo de credito", "python", "estadistica"]},
        {"title": "Gerente de Tesoreria", "company": "Grupo Sura", "mode": "Presencial", "location": "Medellin", "salary": "$16.000.000 - $22.000.000", "required": ["tesoreria", "derivados", "planeacion financiera"]},
        {"title": "Analista SEO/SEM", "company": "Habi", "mode": "Remoto", "location": "Bogota", "salary": "$4.500.000 - $6.500.000", "required": ["google ads", "google analytics", "seo"]},
        {"title": "Content Strategist Mid", "company": "Platzi", "mode": "Remoto", "location": "Bogota", "salary": "$5.500.000 - $8.000.000", "required": ["copywriting", "content marketing", "analitica digital"]},
        {"title": "Growth Marketing Manager", "company": "La Haus", "mode": "Hibrido", "location": "Medellin", "salary": "$9.500.000 - $13.000.000", "required": ["growth", "funnel optimization", "a/b testing"]},
        {"title": "Director de Marketing Digital", "company": "Falabella Colombia", "mode": "Presencial", "location": "Bogota", "salary": "$15.000.000 - $20.000.000", "required": ["estrategia digital", "performance", "liderazgo"]},
        {"title": "Auxiliar de Enfermeria", "company": "Clinica del Country", "mode": "Presencial", "location": "Bogota", "salary": "$2.600.000 - $3.400.000", "required": ["atencion al paciente", "triaje", "historia clinica"]},
        {"title": "Enfermero Jefe UCI", "company": "Fundacion Valle del Lili", "mode": "Presencial", "location": "Cali", "salary": "$5.800.000 - $8.200.000", "required": ["uci", "seguridad del paciente", "protocolos clinicos"]},
        {"title": "Medico General Consulta Externa", "company": "Sanitas", "mode": "Presencial", "location": "Barranquilla", "salary": "$7.000.000 - $10.000.000", "required": ["consulta externa", "rips", "promocion y prevencion"]},
        {"title": "Coordinador de Calidad en Salud", "company": "Nueva EPS", "mode": "Hibrido", "location": "Bogota", "salary": "$9.000.000 - $12.500.000", "required": ["auditoria en salud", "habilitacion", "indicadores de calidad"]},
        {"title": "Auxiliar de Ingenieria de Obra", "company": "Conconcreto", "mode": "Presencial", "location": "Bucaramanga", "salary": "$3.200.000 - $4.600.000", "required": ["autocad", "lectura de planos", "metrados"]},
        {"title": "Residente de Obra Civil", "company": "Amarilo", "mode": "Presencial", "location": "Bogota", "salary": "$6.500.000 - $9.000.000", "required": ["control de obra", "presupuestos", "microsoft project"]},
        {"title": "Ingeniero Estructural Senior", "company": "Constructora Bolivar", "mode": "Hibrido", "location": "Cali", "salary": "$10.500.000 - $14.000.000", "required": ["etabs", "norma nsr-10", "analisis estructural"]},
        {"title": "Gerente de Proyectos de Infraestructura", "company": "Odinsa", "mode": "Presencial", "location": "Barranquilla", "salary": "$17.000.000 - $23.000.000", "required": ["pmp", "gestion de contratos", "gestion de riesgos"]},
    ]

    default_owned = ["python", "sql", "comunicacion"]
    normalized_skills = [s.strip().lower() for s in candidate_skills if isinstance(s, str) and s.strip()]
    if not normalized_skills:
        normalized_skills = default_owned

    results: list[dict[str, Any]] = []
    normalized_preferred = _normalize_location(preferred_location)
    for idx, template in enumerate(templates):
        required = template["required"]
        owned = [skill for skill in required if skill in normalized_skills][:3]
        if len(owned) < 3:
            for skill in normalized_skills:
                if skill not in owned:
                    owned.append(skill)
                if len(owned) == 3:
                    break
        if len(owned) < 3:
            for skill in default_owned:
                if skill not in owned:
                    owned.append(skill)
                if len(owned) == 3:
                    break

        gap = [skill for skill in required if skill not in {s.lower() for s in owned}][:2]
        if not gap:
            gap = [required[-1]]

        score = _score_from_overlap(normalized_skills, required)

        results.append(
            {
                "title": template["title"],
                "company": template["company"],
                "match_percentage": score,
                "salary": template["salary"],
                "mode": _normalize_mode(template["mode"]),
                "location": normalized_preferred,
                "skills_owned": owned[:3],
                "skills_to_develop": gap[:2],
            }
        )

    return results


def _validate_dataset_items(items: Any, candidate_skills: list[str], preferred_location: str) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []

    validated: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        company = str(item.get("company", "")).strip()
        salary = str(item.get("salary", "")).strip()
        if not title or not company or not salary:
            continue

        skills_owned = item.get("skills_owned") if isinstance(item.get("skills_owned"), list) else []
        skills_gap = item.get("skills_to_develop") if isinstance(item.get("skills_to_develop"), list) else []

        owned_clean = [str(s).strip().lower() for s in skills_owned if str(s).strip()][:3]
        if not owned_clean:
            owned_clean = [s for s in candidate_skills[:3]] or ["python", "sql", "comunicacion"]

        gap_clean = [str(s).strip().lower() for s in skills_gap if str(s).strip()][:2]
        if not gap_clean:
            gap_clean = ["analitica"]

        validated.append(
            {
                "title": title,
                "company": company,
                "match_percentage": max(40.0, min(95.0, round(_safe_float(item.get("match_percentage"), 55.0), 1))),
                "salary": salary,
                "mode": _normalize_mode(str(item.get("mode", "Presencial"))),
                "location": preferred_location,
                "skills_owned": owned_clean,
                "skills_to_develop": gap_clean,
            }
        )

    return validated[:20]


def generate_colombia_job_dataset(
    cv_text: str,
    profile_data: Optional[dict[str, Any]] = None,
    preferred_location: str = "Bogota",
) -> list[dict[str, Any]]:
    """Generate 20 realistic job offers for Colombia and personalize by CV skills."""
    skills = []
    experience = 0
    if profile_data:
        skills = profile_data.get("skills", []) or []
        experience = int(profile_data.get("experience_years", 0) or 0)

    candidate_skills = [str(s).strip().lower() for s in skills if str(s).strip()]

    llm = get_llm()
    if llm:
        try:
            prompt = JOB_DATASET_PROMPT.format(
                skills=", ".join(candidate_skills[:12]) or "python, sql, comunicacion",
                location=_normalize_location(preferred_location),
                experience=experience,
            )
            response = llm.invoke(
                [
                    SystemMessage(content="Eres un especialista en reclutamiento de Colombia. Responde solo JSON valido."),
                    HumanMessage(content=prompt),
                ]
            )
            payload = _clean_json_payload(str(response.content))
            items = json.loads(payload)
            validated = _validate_dataset_items(items, candidate_skills, _normalize_location(preferred_location))
            if len(validated) == 20:
                return validated
        except Exception:
            pass

    return _fallback_market_dataset(candidate_skills, _normalize_location(preferred_location))


# Keep backward compatibility
profile_graph = agent_executor
