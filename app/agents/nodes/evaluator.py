from app.agents.state import AgentState

def evaluate_docs(state: AgentState):
    """
    Evaluates the relevance of retrieved documents to the query.
    """
    # Placeholder implementation
    debug_info = state.get("debug_info", {}).copy()
    
    # In a real implementation, this would use an LLM to check relevance
    # For now, we'll use a flag from debug_info for testing, or default to relevant
    relevance = debug_info.get("evaluator_relevance", "relevant")
    debug_info["evaluator"] = f"evaluated as {relevance}"
    
    retry_count = state.get("retry_count", 0)
    if relevance != "relevant":
        retry_count += 1
    
    return {
        "debug_info": debug_info,
        "retry_count": retry_count
    }
