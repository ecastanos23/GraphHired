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
from langchain_google_genai import ChatGoogleGenerativeAI
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
        "summary": "Perfil extraido en modo fallback; configura GEMINI_API_KEY para analisis completo.",
        "profile_gaps": gaps,
        "recommended_roles": ["Software Developer"] if skills else [],
    }


def _generate_content_direct(model_name: str, api_key: str, prompt: str) -> str:
    """Call the Google Generative Language API directly for models without system instructions."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Model returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(str(part.get("text", "")) for part in parts)


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

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {**state, "structured_data": _fallback_structured_profile(text), "error": None}

    prompt = PROFILE_PROMPT.format(cv_text=text[:5000])
    messages = [
        SystemMessage(content="You are an expert CV analyzer."),
        HumanMessage(content=prompt),
    ]

    model_candidates = [settings.GEMINI_MODEL, "gemma-3-1b-it"]
    last_error = ""
    for model_name in dict.fromkeys(model_candidates):
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0,
                max_tokens=500,
                google_api_key=api_key,
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

    try:
        response_text = _generate_content_direct("gemma-3-1b-it", api_key, prompt)
        payload = json.loads(_clean_json_payload(response_text))
        fallback = _fallback_structured_profile(text)
        for key, value in fallback.items():
            payload.setdefault(key, value)
        payload["analysis_model"] = "gemma-3-1b-it"
        return {**state, "structured_data": payload, "error": None}
    except Exception as exc:
        last_error = str(exc)

    fallback = _fallback_structured_profile(text)
    fallback["profile_gaps"] = list(fallback.get("profile_gaps", [])) + [
        "Gemini no respondio por cuota o disponibilidad; se uso extraccion local de respaldo."
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
