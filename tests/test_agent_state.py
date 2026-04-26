from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

def test_agent_state_structure():
    state: AgentState = {
        "query": "test query",
        "rewritten_query": "rewritten test query",
        "chat_history": [HumanMessage(content="hello")],
        "retrieved_docs": [Document(page_content="test doc")],
        "generation": "test generation",
        "retry_count": 0,
        "debug_info": {"test": "info"}
    }
    assert state["query"] == "test query"
    assert len(state["chat_history"]) == 1
    assert isinstance(state["chat_history"][0], HumanMessage)
    assert len(state["retrieved_docs"]) == 1
    assert isinstance(state["retrieved_docs"][0], Document)
    assert state["retry_count"] == 0
    assert state["debug_info"]["test"] == "info"
