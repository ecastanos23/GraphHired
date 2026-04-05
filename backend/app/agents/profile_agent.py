"""
Profile Agent - LangGraph agent for CV analysis and profile extraction
Uses LLM to extract skills, experience, and generate recommendations
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

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


# Keep backward compatibility
profile_graph = agent_executor
