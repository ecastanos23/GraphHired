# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Inicializa el paquete de agentes donde viven los grafos LangGraph y funciones agenticas.

"""Agents module initialization"""
from app.agents.poc_agent import process_text, poc_graph
from app.agents.profile_agent import analyze_profile, profile_graph
from app.agents.matching_agent import match_candidate_to_vacancy, matching_graph
