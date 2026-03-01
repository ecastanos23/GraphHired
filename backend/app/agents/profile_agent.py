"""
Profile Agent - LangGraph agent for CV analysis and profile extraction
Uses LLM to extract skills, experience, and generate recommendations
"""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import os

from app.core.config import settings

class ProfileState(TypedDict):
    """State for profile analysis"""
    cv_text: str
    skills: List[str]
    experience_years: int
    education: Optional[str]
    summary: str
    strengths: List[str]
    recommended_roles: List[str]
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
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None
    
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,  # Deterministic output for consistency
        max_tokens=500,  # Limit tokens for efficiency
        api_key=api_key
    )

def extract_profile_node(state: ProfileState) -> ProfileState:
    """
    Node that extracts profile information from CV using LLM
    Falls back to basic extraction if no API key available
    """
    cv_text = state["cv_text"]
    
    # Try LLM extraction
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
            
            return {
                **state,
                "skills": data.get("skills", []),
                "experience_years": data.get("experience_years", 0),
                "education": data.get("education"),
                "summary": data.get("summary", ""),
                "strengths": data.get("strengths", []),
                "recommended_roles": data.get("recommended_roles", []),
                "error": None
            }
        except Exception as e:
            # Fall through to basic extraction
            pass
    
    # Basic extraction fallback (no LLM)
    return basic_extraction(state)

def basic_extraction(state: ProfileState) -> ProfileState:
    """
    Basic keyword-based extraction when LLM is unavailable
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
    if "senior" in cv_text:
        experience = 5
    elif "mid" in cv_text or "3 years" in cv_text or "4 years" in cv_text:
        experience = 3
    elif "junior" in cv_text or "1 year" in cv_text or "2 years" in cv_text:
        experience = 1
    
    return {
        **state,
        "skills": found_skills[:10],  # Limit to top 10
        "experience_years": experience,
        "education": "Not detected",
        "summary": "Profile analyzed with basic extraction",
        "strengths": found_skills[:3] if found_skills else ["Problem solving"],
        "recommended_roles": ["Software Developer"],
        "error": None
    }

def create_profile_graph() -> StateGraph:
    """Create the profile analysis workflow"""
    workflow = StateGraph(ProfileState)
    
    workflow.add_node("extract", extract_profile_node)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", END)
    
    return workflow.compile()

# Singleton instance
profile_graph = create_profile_graph()

def analyze_profile(cv_text: str) -> dict:
    """
    Analyze CV and extract profile information
    Returns structured profile data
    """
    initial_state: ProfileState = {
        "cv_text": cv_text,
        "skills": [],
        "experience_years": 0,
        "education": None,
        "summary": "",
        "strengths": [],
        "recommended_roles": [],
        "error": None
    }
    
    result = profile_graph.invoke(initial_state)
    
    return {
        "skills": result["skills"],
        "experience_years": result["experience_years"],
        "education": result["education"],
        "summary": result["summary"],
        "strengths": result["strengths"],
        "recommended_roles": result["recommended_roles"]
    }
