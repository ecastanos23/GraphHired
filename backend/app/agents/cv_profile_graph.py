# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Grafo LangGraph para CV PDF. Partes: estado del grafo, prompt, limpieza JSON, fallback local, llamada OpenAI, extraccion PDF y nodos del flujo.

"""
LangGraph workflow for CV parsing and profile extraction from PDF.
"""
from typing import TypedDict, Optional, Dict, Any
import json
import re
import requests

import bleach
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


PROFILE_PROMPT = """Analyze this CV text for a Colombia job-search profile.
Return ONLY valid JSON with this schema:
{{
  "full_name": "candidate name if present",
  "email": "email if present",
  "phone": "phone if present",
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "education": "highest education if present",
  "summary": "short professional summary",
  "profile_gaps": ["missing data needed for job applications"],
  "recommended_roles": ["role1", "role2", "role3"]
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
        "education": None,
        "summary": "Perfil extraido en modo fallback; configura OPENAI_API_KEY para analisis completo.",
        "profile_gaps": gaps,
        "recommended_roles": ["Software Developer"] if skills else [],
    }


def extract_text_node(state: CVProfileState) -> CVProfileState:
    pdf_path = state.get("raw_pdf_path", "")
    try:
        reader = PdfReader(pdf_path)
        text_parts = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(text_parts)
        clean_text = bleach.clean(text, tags=[], attributes={}, strip=True)
        return {**state, "extracted_text": clean_text, "error": None}
    except Exception as exc:
        return {**state, "error": f"Failed to extract PDF text: {exc}"}


def analyze_profile_node(state: CVProfileState) -> CVProfileState:
    if state.get("error"):
        return state

    text = state.get("extracted_text", "")
    if not text.strip():
        return {**state, "error": "Extracted CV text is empty"}

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return {**state, "structured_data": _fallback_structured_profile(text), "error": None}

    prompt = PROFILE_PROMPT.format(cv_text=text[:5000])
    messages = [
        SystemMessage(content="You are an expert CV analyzer."),
        HumanMessage(content=prompt),
    ]

    model_candidates = [settings.OPENAI_MODEL]
    last_error = ""
    for model_name in dict.fromkeys(model_candidates):
        try:
            llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                max_tokens=500,
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
