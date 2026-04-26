import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database.session import get_db

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock()
    yield db

def test_chat_endpoint(mock_db):
    # Mocking graph.invoke
    mock_result = {
        "generation": "Test response",
        "debug_info": {"some": "info"}
    }
    
    with patch("app.api.endpoints.chat.graph") as mock_graph:
        mock_graph.invoke.return_value = mock_result
        
        # Use dependency overrides
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            # 1. Test basic chat
            response = client.post(
                "/chat",
                json={"session_id": "session123", "query": "Hi"}
            )
            
            assert response.status_code == 200
            assert response.json()["response"] == "Test response"
            assert "debug_info" not in response.json()
            
            # Verify DB was called to load history (query for ChatHistory)
            # and called to save history (add twice: user and assistant)
            assert mock_db.add.call_count == 2
            assert mock_db.commit.call_count == 2
            
            # 2. Test chat with debug
            response = client.post(
                "/chat?debug=true",
                json={"session_id": "session123", "query": "Hi"}
            )
            assert response.status_code == 200
            assert "debug_info" in response.json()
            
        finally:
            app.dependency_overrides.clear()
