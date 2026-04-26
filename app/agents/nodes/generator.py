from app.agents.state import AgentState

def generate_answer(state: AgentState):
    """
    Generates an answer based on the retrieved documents and query.
    """
    retrieved_docs = state.get("retrieved_docs", [])
    
    # Placeholder implementation
    # In a real system, we'd pass these docs to an LLM
    response_text = "This is a placeholder answer based on the retrieved documents."
    
    if retrieved_docs:
        response_text += "\n\nSources:"
        for i, doc in enumerate(retrieved_docs):
            source = doc.metadata.get("filename", f"Doc {i+1}")
            page = doc.metadata.get("page_number", "N/A")
            response_text += f"\n- {source} (Page {page})"
    
    debug_info = state.get("debug_info", {}).copy()
    debug_info["generator"] = "generated"
    debug_info["retrieved_docs_count"] = len(retrieved_docs)
    
    return {
        "generation": response_text,
        "debug_info": debug_info
    }
