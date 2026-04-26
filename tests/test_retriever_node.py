import pytest
from unittest.mock import MagicMock, patch
from app.agents.nodes.retriever import retrieve_docs
from langchain_core.documents import Document

@patch("app.agents.nodes.retriever.get_vectorstore")
@patch("app.agents.nodes.retriever.create_hybrid_retriever")
@patch("app.agents.nodes.retriever.OpenAIEmbeddings")
def test_retrieve_docs(mock_embeddings, mock_create_retriever, mock_get_vectorstore):
    # Mocking
    mock_vs = MagicMock()
    mock_get_vectorstore.return_value = mock_vs
    
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = [Document(page_content="test doc", metadata={})]
    mock_create_retriever.return_value = mock_retriever
    
    state = {
        "query": "Who is the CEO?",
        "rewritten_query": "Who is the CEO of RAGentX?",
        "chat_history": [],
        "debug_info": {}
    }
    
    result = retrieve_docs(state)
    
    assert "retrieved_docs" in result
    assert len(result["retrieved_docs"]) == 1
    assert result["retrieved_docs"][0].page_content == "test doc"
    assert result["debug_info"]["retrieved_docs_count"] == 1
    
    # Ensure it used the rewritten query
    mock_retriever.invoke.assert_called_once_with("Who is the CEO of RAGentX?")
