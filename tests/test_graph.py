import pytest
from app.agents.state import AgentState
from unittest.mock import patch, MagicMock
import importlib
import app.agents.graph
from langgraph.graph import END

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
        "debug_info": {"evaluator_relevance": "irrelevant"},
        "retry_count": 0
    }
    assert decide_to_generate(state_retry) == "rewrite"
    
    # Case 3: Not relevant, retry_count >= 3
    state_max_retries: AgentState = {
        "debug_info": {"evaluator_relevance": "irrelevant"},
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
    assert decide_to_finish(state_valid) == END
    
    # Case 2: Invalid generation
    state_invalid: AgentState = {
        "debug_info": {"validator_status": "invalid"}
    }
    assert decide_to_finish(state_invalid) == "generate"

def test_graph_flow_mocked():
    """
    Tests the full graph flow with mocked nodes.
    """
    # Patch all nodes to avoid LLM calls and ensure deterministic behavior
    with patch("app.agents.nodes.rewriter.rewrite_query") as mock_rewrite, \
         patch("app.agents.nodes.retriever.retrieve_docs") as mock_retrieve, \
         patch("app.agents.nodes.evaluator.evaluate_docs") as mock_evaluate, \
         patch("app.agents.nodes.generator.generate_answer") as mock_generate, \
         patch("app.agents.nodes.validator.validate_generation") as mock_validate:
        
        # Reload graph to pick up mocked nodes
        importlib.reload(app.agents.graph)
        from app.agents.graph import graph
        
        # Setup mocks
        mock_rewrite.side_effect = lambda state: {"rewritten_query": "rewritten", "debug_info": {**state.get("debug_info", {}), "rewriter": "done"}}
        mock_retrieve.side_effect = lambda state: {"retrieved_docs": [], "debug_info": {**state.get("debug_info", {}), "retriever": "done"}}
        mock_evaluate.side_effect = lambda state: {"debug_info": {**state.get("debug_info", {}), "evaluator_relevance": "relevant"}}
        mock_generate.side_effect = lambda state: {"generation": "mocked answer", "debug_info": {**state.get("debug_info", {}), "generator_status": "completed"}}
        mock_validate.side_effect = lambda state: {"debug_info": {**state.get("debug_info", {}), "validator_status": "valid"}}
        
        initial_state: AgentState = {
            "query": "test query",
            "chat_history": [],
            "retry_count": 0,
            "debug_info": {}
        }
        
        result = graph.invoke(initial_state)
        
        assert "generation" in result
        assert result["debug_info"]["evaluator_relevance"] == "relevant"
        assert result["debug_info"]["validator_status"] == "valid"
        assert mock_rewrite.call_count == 1
        assert mock_retrieve.call_count == 1
        assert mock_evaluate.call_count == 1
        assert mock_generate.call_count == 1
        assert mock_validate.call_count == 1

def test_graph_retry_flow_mocked():
    """
    Tests the retry flow in the graph.
    """
    with patch("app.agents.nodes.rewriter.rewrite_query") as mock_rewrite, \
         patch("app.agents.nodes.retriever.retrieve_docs") as mock_retrieve, \
         patch("app.agents.nodes.evaluator.evaluate_docs") as mock_evaluate, \
         patch("app.agents.nodes.generator.generate_answer") as mock_generate, \
         patch("app.agents.nodes.validator.validate_generation") as mock_validate:
        
        # Reload graph to pick up mocked nodes
        importlib.reload(app.agents.graph)
        from app.agents.graph import graph
        
        # Setup mocks
        mock_rewrite.side_effect = lambda state: {"rewritten_query": f"rewritten {state.get('retry_count', 0)}", "debug_info": {**state.get("debug_info", {}), "rewriter": "done"}}
        mock_retrieve.side_effect = lambda state: {"retrieved_docs": [], "debug_info": {**state.get("debug_info", {}), "retriever": "done"}}
        
        # Mock evaluate to increment retry count and stay irrelevant for 3 times
        def mock_evaluate_side_effect(state):
            count = state.get("retry_count", 0)
            if count < 3:
                return {
                    "debug_info": {**state.get("debug_info", {}), "evaluator_relevance": "irrelevant"},
                    "retry_count": count + 1
                }
            else:
                return {
                    "debug_info": {**state.get("debug_info", {}), "evaluator_relevance": "relevant"},
                    "retry_count": count
                }
        mock_evaluate.side_effect = mock_evaluate_side_effect
        
        mock_generate.side_effect = lambda state: {"generation": "mocked answer", "debug_info": {**state.get("debug_info", {}), "generator_status": "completed"}}
        mock_validate.side_effect = lambda state: {"debug_info": {**state.get("debug_info", {}), "validator_status": "valid"}}

        initial_state: AgentState = {
            "query": "test query",
            "chat_history": [],
            "retry_count": 0,
            "debug_info": {}
        }
        
        result = graph.invoke(initial_state)
        
        # It should have retried 2 times (total 3 attempts), then moved to generate on the 3rd evaluate call (retry_count=3)
        assert result["retry_count"] == 3
        assert mock_rewrite.call_count == 3 # Initial call + 2 retries
        assert mock_retrieve.call_count == 3
        assert mock_evaluate.call_count == 3
        assert mock_generate.call_count == 1
