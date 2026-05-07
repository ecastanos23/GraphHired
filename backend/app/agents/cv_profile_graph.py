# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Grafo LangGraph para CV PDF. Partes: estado del grafo, prompt, limpieza JSON, fallback local, llamada OpenAI, extraccion PDF y nodos del flujo.

"""
LangGraph workflow for CV parsing and profile extraction from PDF.
"""
from typing import TypedDict, Optional, Dict, Any
import base64
import json
import re

import bleach
import fitz
from PyPDF2 import PdfReader
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings


class CVProfileState(TypedDict):
    raw_pdf_path: str
    extracted_text: str
    structured_data: Dict[str, Any]
    error: Optional[str]


VISION_PAGE_LIMIT = 6
VISION_RENDER_ZOOM = 2.0
VISION_MIN_TEXT_LENGTH = 250


PROFILE_PROMPT = """Extract a complete, structured professional profile from the CV text below. Return ONLY valid JSON.

EXTRACTION RULES - Be thorough and explicit:
1. full_name: Extract complete name (first + last names).
2. contact: Extract all contact info. LOCATION: Look for city names after phone, email, or with keywords like "Medellín - Colombia", "Bogotá", "Cali", etc. If no explicit location, infer from context (company locations, university cities). Default to null if truly not found.
3. summary: Combine "Resumen personal" or intro sections; max 3 sentences capturing key strengths.
4. experience_years: Calculate total years of professional experience (today - earliest start date).
5. experience: For EACH job, extract:
   - role: Job title (e.g. "McDonald's Cashier", "Software Developer")
   - company: Company name
   - start_date: Start month/year (e.g. "2024-05")
   - end_date: End month/year or "present" if current
   - duration: Calculated years (e.g. 0.3 for 3 months)
   - description: 1-2 line bullet list of main duties/accomplishments
6. education: For EACH degree/course, extract:
   - degree: Degree type (e.g. "Ingeniería de Sistemas", "Técnico Laboral", "Bachillerato")
   - field: Field of study if applicable
   - institution: School/university name
   - year: Graduation year or "en curso" if ongoing
   - description: Duration or key info (e.g. "88 horas")
7. skills: List EXPLICITLY mentioned technical skills (not soft skills). Normalize to lowercase.
8. languages: Extract language + proficiency level. If not stated, infer from context.
9. certifications: Courses, seminars, certifications (separate from degrees).
10. profile_gaps: List missing critical info (salary expectations, availability, work preferences).
11. recommended_roles: Suggest 2-3 roles based on skills + experience.

Return ONLY this JSON schema (no explanations):
{{
    "full_name": string | null,
    "contact": {{ "email": string | null, "phone": string | null, "location": string | null }},
    "summary": string | null,
    "experience_years": number,
    "experience": [
        {{
            "role": string,
            "company": string | null,
            "start_date": string | null,
            "end_date": string | null,
            "duration": number | null,
            "description": string | null
        }}
    ],
    "education": [
        {{
            "degree": string | null,
            "field": string | null,
            "institution": string | null,
            "year": string | number | null,
            "description": string | null
        }}
    ],
    "skills": string[],
    "languages": [ {{ "language": string, "level": string | null }} ],
    "certifications": [ {{ "name": string, "issuer": string | null, "year": string | null }} ],
    "profile_gaps": string[],
    "recommended_roles": string[]
}}

CV TEXT:
{cv_text}
"""


def _clean_json_payload(raw_content: str) -> str:
    text = str(raw_content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx >= 0 and end_idx > start_idx:
        return text[start_idx : end_idx + 1]
    return text


def _fallback_structured_profile(text: str) -> Dict[str, Any]:
    lower_text = text.lower()
    email_match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", text)
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    skills_catalog = [
        "python", "javascript", "typescript", "react", "next.js", "fastapi",
        "sql", "postgresql", "docker", "aws", "excel", "power bi", "figma",
        "node.js", "java", "scrum", "liderazgo", "marketing", "ventas",
    ]
    skills = [skill for skill in skills_catalog if skill in lower_text]
    gaps = []
    if not email_match:
        gaps.append("Falta correo de contacto")
    if not phone_match:
        gaps.append("Falta telefono de contacto")
    if "salario" not in lower_text and "aspiracion" not in lower_text:
        gaps.append("Falta aspiracion salarial")
    if "remoto" not in lower_text and "hibrido" not in lower_text and "presencial" not in lower_text:
        gaps.append("Falta modalidad preferida")
    return {
        "full_name": None,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "skills": skills[:12],
        "experience_years": 0,
        "education": [],  # Return empty list, not None
        "experience": [],  # Return empty list
        "languages": [],  # Return empty list
        "certifications": [],  # Return empty list
        "summary": "Perfil extraido en modo fallback; configura OPENAI_API_KEY para analisis completo.",
        "profile_gaps": gaps,
        "recommended_roles": ["Software Developer"] if skills else [],
    }


def _extract_text_with_pypdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text_parts = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(text_parts)
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def _render_pdf_pages_as_data_urls(pdf_path: str, max_pages: int = VISION_PAGE_LIMIT) -> list[str]:
    data_urls: list[str] = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            if page_index >= max_pages:
                break
            pixmap = page.get_pixmap(matrix=fitz.Matrix(VISION_RENDER_ZOOM, VISION_RENDER_ZOOM), alpha=False)
            encoded = base64.b64encode(pixmap.tobytes("png")).decode("ascii")
            data_urls.append(f"data:image/png;base64,{encoded}")
    return data_urls


def _transcribe_pdf_with_vision(pdf_path: str, api_key: str, model_name: str) -> str:
    image_urls = _render_pdf_pages_as_data_urls(pdf_path)
    if not image_urls:
        return ""

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        max_tokens=2000,
        api_key=api_key,
    )

    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "Transcribe the attached CV pages into clean plain text. "
                "Preserve headings, bullets, emails, phone numbers, dates, tables hints, and original section order. "
                "Insert a page separator line exactly like '---PAGE {n}---' before each page's content. "
                "Do NOT summarize, interpret, or add labels — return only the verbatim extracted text with separators."
            ),
        }
    ]
    for page_index, image_url in enumerate(image_urls, start=1):
        content.append({"type": "text", "text": f"Page {page_index}"})
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    response = llm.invoke(
        [
            SystemMessage(content="You are a precise OCR engine specialized in CVs."),
            HumanMessage(content=content),
        ]
    )
    return str(response.content or "").strip()


def extract_text_node(state: CVProfileState) -> CVProfileState:
    pdf_path = state.get("raw_pdf_path", "")
    api_key = settings.OPENAI_API_KEY
    vision_error = None
    direct_text_error = None

    # Priority 1: Try vision-based OCR transcription first (handles complex layouts like Canva)
    if api_key:
        try:
            vision_text = _transcribe_pdf_with_vision(pdf_path, api_key, settings.OPENAI_MODEL)
            if vision_text:
                return {**state, "extracted_text": vision_text, "error": None}
        except Exception as exc:
            vision_error = f"Vision transcription failed: {exc}"

    # Priority 2: Fallback to direct PyPDF2 text extraction if vision unavailable or failed
    try:
        direct_text = _extract_text_with_pypdf(pdf_path)
        if direct_text:
            return {**state, "extracted_text": direct_text, "error": None}
    except Exception as exc:
        direct_text_error = f"Direct PDF text extraction failed: {exc}"

    # Both methods failed; report the most informative error
    error_msg = vision_error or direct_text_error or "Failed to extract PDF text"
    return {**state, "error": error_msg}


def analyze_profile_node(state: CVProfileState) -> CVProfileState:
    if state.get("error"):
        return state

    text = state.get("extracted_text", "")
    if not text.strip():
        return {**state, "error": "Extracted CV text is empty"}

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return {**state, "structured_data": _fallback_structured_profile(text), "error": None}

    prompt = PROFILE_PROMPT.format(cv_text=text[:8000])  # Increased from 5000 to preserve more context
    messages = [
        SystemMessage(content="You are an expert CV analyzer. Extract and structure ALL relevant information precisely."),
        HumanMessage(content=prompt),
    ]

    model_candidates = [settings.OPENAI_MODEL]
    last_error = ""
    for model_name in dict.fromkeys(model_candidates):
        try:
            llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                max_tokens=1500,  # Increased from 500 to allow detailed JSON responses
                api_key=api_key,
            )
            response = llm.invoke(messages)
            payload = json.loads(_clean_json_payload(str(response.content)))
            fallback = _fallback_structured_profile(text)
            for key, value in fallback.items():
                payload.setdefault(key, value)
            payload["analysis_model"] = model_name
            return {**state, "structured_data": payload, "error": None}
        except Exception as exc:
            last_error = str(exc)

    fallback = _fallback_structured_profile(text)
    fallback["profile_gaps"] = list(fallback.get("profile_gaps", [])) + [
        "OpenAI no respondio; se uso extraccion local de respaldo."
    ]
    fallback["summary"] = f"{fallback['summary']} Motivo IA: {last_error[:180]}"
    return {**state, "structured_data": fallback, "error": None}


def create_cv_profile_graph() -> StateGraph:
    workflow = StateGraph(CVProfileState)
    workflow.add_node("extract_text", extract_text_node)
    workflow.add_node("analyze_profile", analyze_profile_node)

    workflow.set_entry_point("extract_text")
    workflow.add_edge("extract_text", "analyze_profile")
    workflow.add_edge("analyze_profile", END)

    return workflow.compile()


cv_profile_graph = create_cv_profile_graph()
