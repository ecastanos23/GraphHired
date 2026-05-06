# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Grafo semantico para embeddings. Partes: sanitizacion del texto candidato, generacion de embedding y compilacion del grafo.

"""
LangGraph workflow for candidate semantic matching preparation.
Each node receives and returns state.
"""
from typing import TypedDict, Optional, List

import bleach
from langgraph.graph import StateGraph, END
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


class SemanticMatchState(TypedDict):
    candidate_text: str
    sanitized_text: str
    candidate_embedding: Optional[List[float]]
    error: Optional[str]


def sanitize_candidate_text_node(state: SemanticMatchState) -> SemanticMatchState:
    """Clean user-provided candidate text before embedding."""
    cleaned = bleach.clean(state.get("candidate_text", ""), tags=[], attributes={}, strip=True).strip()
    return {**state, "sanitized_text": cleaned}


def embed_candidate_text_node(state: SemanticMatchState) -> SemanticMatchState:
    """Generate OpenAI embedding vector for candidate text."""
    text = state.get("sanitized_text", "")
    api_key = settings.OPENAI_API_KEY
    if not text:
        return {**state, "error": "Candidate text is empty", "candidate_embedding": None}
    if not api_key:
        return {**state, "error": "OPENAI_API_KEY is not configured", "candidate_embedding": None}

    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=api_key,
    )

    vector = embeddings.embed_query(text)
    return {**state, "candidate_embedding": vector, "error": None}


def create_semantic_matching_graph() -> StateGraph:
    workflow = StateGraph(SemanticMatchState)
    workflow.add_node("sanitize_text", sanitize_candidate_text_node)
    workflow.add_node("embed_candidate", embed_candidate_text_node)

    workflow.set_entry_point("sanitize_text")
    workflow.add_edge("sanitize_text", "embed_candidate")
    workflow.add_edge("embed_candidate", END)

    return workflow.compile()


semantic_matching_graph = create_semantic_matching_graph()
