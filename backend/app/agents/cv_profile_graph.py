"""
LangGraph workflow for CV parsing and profile extraction from PDF.
"""
from typing import TypedDict, Optional, Dict, Any
import json

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


PROFILE_PROMPT = """Analyze this CV text and return ONLY valid JSON with this schema:
{
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "summary": "short summary"
}

CV TEXT:
{cv_text}
"""


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
        skills = []
        if "python" in text.lower():
            skills.append("Python")
        if "fastapi" in text.lower():
            skills.append("FastAPI")
        return {
            **state,
            "structured_data": {
                "skills": skills,
                "experience_years": 0,
                "summary": "Profile extracted without LLM (fallback mode)",
            },
            "error": None,
        }

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,
        max_tokens=500,
        google_api_key=api_key,
    )

    prompt = PROFILE_PROMPT.format(cv_text=text[:5000])
    messages = [
        SystemMessage(content="You are an expert CV analyzer."),
        HumanMessage(content=prompt),
    ]

    try:
        response = llm.invoke(messages)
        payload = json.loads(response.content)
        return {**state, "structured_data": payload, "error": None}
    except Exception as exc:
        return {**state, "error": f"Failed to analyze profile: {exc}"}


def create_cv_profile_graph() -> StateGraph:
    workflow = StateGraph(CVProfileState)
    workflow.add_node("extract_text", extract_text_node)
    workflow.add_node("analyze_profile", analyze_profile_node)

    workflow.set_entry_point("extract_text")
    workflow.add_edge("extract_text", "analyze_profile")
    workflow.add_edge("analyze_profile", END)

    return workflow.compile()


cv_profile_graph = create_cv_profile_graph()
