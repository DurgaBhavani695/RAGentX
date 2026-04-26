import pytest
from app.agents.nodes.retriever import retrieve_docs
from app.agents.state import AgentState
from langchain_core.documents import Document

def test_retrieve_docs_with_web_search_flag(mocker):
    # Mock DuckDuckGoSearchRun
    mock_ddg = mocker.patch("app.agents.nodes.retriever.DuckDuckGoSearchRun")
    mock_instance = mock_ddg.return_value
    mock_instance.run.return_value = "Mocked web search result"

    # Initial state with web search flag set to True
    state: AgentState = {
        "query": "Who is the current CEO of Microsoft?",
        "rewritten_query": "current CEO Microsoft",
        "chat_history": [],
        "retrieved_docs": [],
        "generation": "",
        "retry_count": 0,
        "debug_info": {},
        "use_web_search": True
    }

    # Execute the node
    result = retrieve_docs(state)

    # Verify DuckDuckGo was called
    mock_instance.run.assert_called_once_with("current CEO Microsoft")
    
    # Verify that we have more docs or a specific web search doc
    assert len(result["retrieved_docs"]) > 0
    # Check if any doc contains the mocked result
    assert any("Mocked web search result" in doc.page_content for doc in result["retrieved_docs"])

def test_retrieve_docs_without_web_search_flag(mocker):
    # Mock DuckDuckGoSearchRun to ensure it's NOT called
    mock_ddg = mocker.patch("app.agents.nodes.retriever.DuckDuckGoSearchRun")
    
    state: AgentState = {
        "query": "Who is the current CEO of Microsoft?",
        "rewritten_query": "current CEO Microsoft",
        "chat_history": [],
        "retrieved_docs": [],
        "generation": "",
        "retry_count": 0,
        "debug_info": {},
        "use_web_search": False
    }

    result = retrieve_docs(state)

    # Verify DuckDuckGo was NOT called
    assert not mock_ddg.called
    assert "retrieved_docs" in result
