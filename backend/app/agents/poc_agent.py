# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Agente PoC. Partes: estado simple, nodo que transforma texto, grafo LangGraph minimo y funcion de procesamiento para probar el pipeline.

"""
PoC Agent - Basic LangGraph node for Hello World testing
Demonstrates LangGraph integration with a simple text transformation
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class PoCState(TypedDict):
    """State for the PoC graph"""
    input_text: str
    output_text: str

def uppercase_node(state: PoCState) -> PoCState:
    """
    Simple node that converts text to uppercase
    This demonstrates a basic LangGraph transformation
    """
    return {
        "input_text": state["input_text"],
        "output_text": state["input_text"].upper()
    }

def create_poc_graph() -> StateGraph:
    """
    Create the PoC workflow graph
    Single node that transforms text to uppercase
    """
    # Create the graph
    workflow = StateGraph(PoCState)
    
    # Add the uppercase node
    workflow.add_node("uppercase", uppercase_node)
    
    # Set entry point
    workflow.set_entry_point("uppercase")
    
    # Add edge to END
    workflow.add_edge("uppercase", END)
    
    # Compile the graph
    return workflow.compile()

# Create singleton instance
poc_graph = create_poc_graph()

def process_text(text: str) -> str:
    """
    Process text through the PoC LangGraph
    Returns the uppercase version of the input
    """
    result = poc_graph.invoke({"input_text": text, "output_text": ""})
    return result["output_text"]
