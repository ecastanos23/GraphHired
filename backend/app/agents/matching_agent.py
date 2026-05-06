# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Agente de matching. Partes: estado LangGraph, calculo de skills, experiencia, salario, modalidad, score total y funcion publica de comparacion.

"""
Matching Agent - Semantic matching between candidates and vacancies
Uses embeddings for similarity search and rule-based filtering
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import OpenAIEmbeddings
from decimal import Decimal
import numpy as np

from app.core.config import settings

class MatchState(TypedDict):
    """State for matching workflow"""
    candidate_skills: List[str]
    candidate_experience: int
    candidate_salary: Optional[Decimal]
    candidate_modality: Optional[str]
    candidate_location: Optional[str]
    vacancy_skills: List[str]
    vacancy_experience: int
    vacancy_salary_min: Optional[Decimal]
    vacancy_salary_max: Optional[Decimal]
    vacancy_modality: Optional[str]
    vacancy_location: Optional[str]
    skill_score: float
    experience_score: float
    salary_score: float
    modality_score: float
    total_score: float
    matching_skills: List[str]
    missing_skills: List[str]

def get_embeddings():
    """Get embeddings instance"""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=api_key
    )

def calculate_skill_match(state: MatchState) -> MatchState:
    """Node to calculate skill matching score"""
    candidate_skills = set(s.lower() for s in state["candidate_skills"])
    vacancy_skills = set(s.lower() for s in state["vacancy_skills"])
    
    if not vacancy_skills:
        return {**state, "skill_score": 100.0, "matching_skills": [], "missing_skills": []}
    
    matching = candidate_skills.intersection(vacancy_skills)
    missing = vacancy_skills - candidate_skills
    
    score = (len(matching) / len(vacancy_skills)) * 100 if vacancy_skills else 0
    
    return {
        **state,
        "skill_score": round(score, 2),
        "matching_skills": list(matching),
        "missing_skills": list(missing)
    }

def calculate_experience_match(state: MatchState) -> MatchState:
    """Node to calculate experience matching score"""
    candidate_exp = state["candidate_experience"]
    required_exp = state["vacancy_experience"]
    
    if required_exp == 0:
        score = 100.0
    elif candidate_exp >= required_exp:
        score = 100.0
    else:
        score = (candidate_exp / required_exp) * 100
    
    return {**state, "experience_score": round(score, 2)}

def calculate_salary_match(state: MatchState) -> MatchState:
    """Node to calculate salary compatibility"""
    expected = state["candidate_salary"]
    salary_min = state["vacancy_salary_min"]
    salary_max = state["vacancy_salary_max"]
    
    if not expected or (not salary_min and not salary_max):
        return {**state, "salary_score": 100.0}
    
    expected_float = float(expected)
    
    if salary_min and salary_max:
        min_float = float(salary_min)
        max_float = float(salary_max)
        
        if min_float <= expected_float <= max_float:
            score = 100.0
        elif expected_float < min_float:
            score = 100.0  # Candidate expects less - good for employer
        else:
            # Candidate expects more
            diff_percent = ((expected_float - max_float) / max_float) * 100
            score = max(0, 100 - diff_percent)
    else:
        score = 80.0  # Partial info
    
    return {**state, "salary_score": round(score, 2)}

def calculate_modality_match(state: MatchState) -> MatchState:
    """Node to calculate work modality compatibility"""
    candidate_mod = state["candidate_modality"]
    vacancy_mod = state["vacancy_modality"]
    
    if not candidate_mod or not vacancy_mod:
        return {**state, "modality_score": 100.0}
    
    if candidate_mod == vacancy_mod:
        score = 100.0
    elif vacancy_mod == "hybrid":
        score = 80.0  # Hybrid can accommodate both
    elif candidate_mod == "hybrid":
        score = 70.0  # Candidate flexible
    else:
        score = 30.0  # Mismatch
    
    return {**state, "modality_score": round(score, 2)}

def calculate_total_score(state: MatchState) -> MatchState:
    """Node to calculate weighted total score"""
    # Weights for each factor
    weights = {
        "skill": 0.40,
        "experience": 0.25,
        "salary": 0.20,
        "modality": 0.15
    }
    
    total = (
        state["skill_score"] * weights["skill"] +
        state["experience_score"] * weights["experience"] +
        state["salary_score"] * weights["salary"] +
        state["modality_score"] * weights["modality"]
    )
    
    return {**state, "total_score": round(total, 2)}

def create_matching_graph() -> StateGraph:
    """Create the matching workflow"""
    workflow = StateGraph(MatchState)
    
    workflow.add_node("skill_match", calculate_skill_match)
    workflow.add_node("experience_match", calculate_experience_match)
    workflow.add_node("salary_match", calculate_salary_match)
    workflow.add_node("modality_match", calculate_modality_match)
    workflow.add_node("calculate_total_score", calculate_total_score)
    
    workflow.set_entry_point("skill_match")
    workflow.add_edge("skill_match", "experience_match")
    workflow.add_edge("experience_match", "salary_match")
    workflow.add_edge("salary_match", "modality_match")
    workflow.add_edge("modality_match", "calculate_total_score")
    workflow.add_edge("calculate_total_score", END)
    
    return workflow.compile()

# Singleton instance
matching_graph = create_matching_graph()

def match_candidate_to_vacancy(
    candidate_skills: List[str],
    candidate_experience: int,
    candidate_salary: Optional[Decimal],
    candidate_modality: Optional[str],
    candidate_location: Optional[str],
    vacancy_skills: List[str],
    vacancy_experience: int,
    vacancy_salary_min: Optional[Decimal],
    vacancy_salary_max: Optional[Decimal],
    vacancy_modality: Optional[str],
    vacancy_location: Optional[str]
) -> dict:
    """
    Match a candidate profile against a vacancy
    Returns match scores and analysis
    """
    initial_state: MatchState = {
        "candidate_skills": candidate_skills,
        "candidate_experience": candidate_experience,
        "candidate_salary": candidate_salary,
        "candidate_modality": candidate_modality,
        "candidate_location": candidate_location,
        "vacancy_skills": vacancy_skills,
        "vacancy_experience": vacancy_experience,
        "vacancy_salary_min": vacancy_salary_min,
        "vacancy_salary_max": vacancy_salary_max,
        "vacancy_modality": vacancy_modality,
        "vacancy_location": vacancy_location,
        "skill_score": 0.0,
        "experience_score": 0.0,
        "salary_score": 0.0,
        "modality_score": 0.0,
        "total_score": 0.0,
        "matching_skills": [],
        "missing_skills": []
    }
    
    result = matching_graph.invoke(initial_state)
    
    return {
        "total_score": result["total_score"],
        "skill_score": result["skill_score"],
        "experience_score": result["experience_score"],
        "salary_score": result["salary_score"],
        "modality_score": result["modality_score"],
        "matching_skills": result["matching_skills"],
        "missing_skills": result["missing_skills"]
    }
