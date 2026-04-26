from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes.rewriter import rewrite_query
from app.agents.nodes.retriever import retrieve_docs
from app.agents.nodes.evaluator import evaluate_docs
from app.agents.nodes.generator import generate_answer
from app.agents.nodes.validator import validate_generation

def decide_to_generate(state: AgentState):
    """
    Determines whether to generate an answer or rewrite the query.
    """
    # Logic from task:
    # If docs are relevant -> generate
    # If docs are NOT relevant and retry_count < 3 -> rewrite
    # Else -> generate
    
    # For now, evaluate_docs placeholder doesn't set relevance.
    # We'll assume relevance is checked here or in evaluate_docs.
    # Let's check debug_info for evaluator's decision.
    evaluator_decision = state.get("debug_info", {}).get("evaluator_relevance", "relevant")
    retry_count = state.get("retry_count", 0)
    
    if evaluator_decision == "relevant":
        return "generate"
    elif retry_count < 3:
        # Increment retry count for the next attempt
        # Note: In LangGraph, we return the next node name, 
        # and the node itself should update the state.
        # However, conditional edges can also return a state update if using a specific pattern,
        # but usually they just return the next node.
        return "rewrite"
    else:
        return "generate"

def decide_to_finish(state: AgentState):
    """
    Determines whether to finish or regenerate.
    """
    validator_decision = state.get("debug_info", {}).get("validator_status", "valid")
    
    if validator_decision == "valid":
        return END
    else:
        return "generate"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("rewrite", rewrite_query)
workflow.add_node("retrieve", retrieve_docs)
workflow.add_node("evaluate", evaluate_docs)
workflow.add_node("generate", generate_answer)
workflow.add_node("validate", validate_generation)

# Set entry point
workflow.add_edge(START, "rewrite")

# Define flow
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("retrieve", "evaluate")

# Conditional edges for evaluate
workflow.add_conditional_edges(
    "evaluate",
    decide_to_generate,
    {
        "generate": "generate",
        "rewrite": "rewrite"
    }
)

# Conditional edges for validate
workflow.add_conditional_edges(
    "validate",
    decide_to_finish,
    {
        END: END,
        "generate": "generate"
    }
)

# Bridge generate to validate
workflow.add_edge("generate", "validate")

# Compile
graph = workflow.compile()
