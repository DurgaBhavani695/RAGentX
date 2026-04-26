import pytest
from unittest.mock import MagicMock, patch
from app.agents.nodes.rewriter import rewrite_query
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

def test_rewrite_query_success():
    # Setup state
    state: AgentState = {
        "query": "What is the weather?",
        "rewritten_query": "",
        "chat_history": [
            HumanMessage(content="I am in London."),
            AIMessage(content="Hello!")
        ],
        "retrieved_docs": [],
        "generation": "",
        "retry_count": 0,
        "debug_info": {}
    }

    # Mock LLM response
    mock_llm = MagicMock(spec=ChatOpenAI)
    mock_llm.invoke.return_value = AIMessage(content="What is the weather in London?")

    with patch("app.agents.nodes.rewriter.get_llm", return_value=mock_llm):
        result = rewrite_query(state)

    assert result["rewritten_query"] == "What is the weather in London?"
    assert "rewriter" in result["debug_info"]
    assert result["debug_info"]["rewriter"] == "What is the weather in London?"

def test_rewrite_query_no_history():
    # Setup state
    state: AgentState = {
        "query": "Hello",
        "rewritten_query": "",
        "chat_history": [],
        "retrieved_docs": [],
        "generation": "",
        "retry_count": 0,
        "debug_info": {}
    }

    # Mock LLM response
    mock_llm = MagicMock(spec=ChatOpenAI)
    mock_llm.invoke.return_value = AIMessage(content="Hello")

    with patch("app.agents.nodes.rewriter.get_llm", return_value=mock_llm):
        result = rewrite_query(state)

    assert result["rewritten_query"] == "Hello"
