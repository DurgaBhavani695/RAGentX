import pytest
from app.agents.state import AgentState

def test_graph_structure():
    """
    Verifies that the compiled graph has the correct nodes and structure.
    """
    from app.agents.graph import graph
    # Verify that it's a compiled graph (has the invoke method)
    assert hasattr(graph, "invoke")
    
    # Verify nodes are present
    nodes = graph.get_graph().nodes
    
    expected_nodes = ["rewrite", "retrieve", "evaluate", "generate", "validate"]
    for node_name in expected_nodes:
        assert node_name in nodes

def test_decide_to_generate():
    """
    Tests the routing logic after evaluation.
    """
    from app.agents.graph import decide_to_generate
    # Case 1: Relevant docs
    state_relevant: AgentState = {
        "debug_info": {"evaluator_relevance": "relevant"},
        "retry_count": 0
    }
    assert decide_to_generate(state_relevant) == "generate"
    
    # Case 2: Not relevant, retry_count < 3
    state_retry: AgentState = {
        "debug_info": {"evaluator_relevance": "not_relevant"},
        "retry_count": 0
    }
    assert decide_to_generate(state_retry) == "rewrite"
    
    # Case 3: Not relevant, retry_count >= 3
    state_max_retries: AgentState = {
        "debug_info": {"evaluator_relevance": "not_relevant"},
        "retry_count": 3
    }
    assert decide_to_generate(state_max_retries) == "generate"

def test_decide_to_finish():
    """
    Tests the routing logic after validation.
    """
    from app.agents.graph import decide_to_finish
    # Case 1: Valid generation
    state_valid: AgentState = {
        "debug_info": {"validator_status": "valid"}
    }
    from langgraph.graph import END
    assert decide_to_finish(state_valid) == END
    
    # Case 2: Invalid generation
    state_invalid: AgentState = {
        "debug_info": {"validator_status": "invalid"}
    }
    assert decide_to_finish(state_invalid) == "generate"

from unittest.mock import patch, MagicMock

def test_graph_flow_mocked():
    """
    Tests the full graph flow with mocked nodes.
    """
    # Patch before importing graph so the graph gets the mocks
    with patch("app.agents.nodes.rewriter.rewrite_query") as mock_rewrite, \
         patch("app.agents.nodes.retriever.retrieve_docs") as mock_retrieve:
        
        from app.agents.graph import graph
        
        # Setup mocks
        mock_rewrite.side_effect = lambda state: {"rewritten_query": "rewritten", "debug_info": {**state.get("debug_info", {}), "rewriter": "done"}}
        mock_retrieve.side_effect = lambda state: {"retrieved_docs": [], "debug_info": {**state.get("debug_info", {}), "retriever": "done"}}
        
        # Test 1: Straight through to END
        initial_state: AgentState = {
            "query": "test query",
            "chat_history": [],
            "retry_count": 0,
            "debug_info": {
                "evaluator_relevance": "relevant",
                "validator_status": "valid"
            }
        }
        
        result = graph.invoke(initial_state)
        
        assert "generation" in result
        assert result["debug_info"]["evaluator"] == "evaluated as relevant"
        assert result["debug_info"]["validator"] == "validated as valid"
        assert mock_rewrite.call_count == 1
        assert mock_retrieve.call_count == 1

def test_graph_retry_flow_mocked():
    """
    Tests the retry flow in the graph.
    """
    # Note: We need a fresh graph or at least fresh mocks
    # Since graph is already imported in the previous test, we might need to reload it or patch differently.
    # But let's see if this works first.
    
    with patch("app.agents.nodes.rewriter.rewrite_query") as mock_rewrite, \
         patch("app.agents.nodes.retriever.retrieve_docs") as mock_retrieve:
        
        from app.agents.graph import graph
        
        # Setup mocks
        mock_rewrite.side_effect = lambda state: {"rewritten_query": f"rewritten {state.get('retry_count', 0)}", "debug_info": {**state.get("debug_info", {}), "rewriter": "done"}}
        mock_retrieve.side_effect = lambda state: {"retrieved_docs": [], "debug_info": {**state.get("debug_info", {}), "retriever": "done"}}
        
        initial_state: AgentState = {
            "query": "test query",
            "chat_history": [],
            "retry_count": 0,
            "debug_info": {
                "evaluator_relevance": "not_relevant",
                "validator_status": "valid"
            }
        }
        
        result = graph.invoke(initial_state)
        
        assert result["retry_count"] >= 3
        assert mock_rewrite.call_count >= 3
