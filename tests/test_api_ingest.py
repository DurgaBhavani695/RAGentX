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

def test_ingest_text(mock_db):
    # Mocking dependencies
    mock_vs_instance = MagicMock()
    
    with patch("app.api.endpoints.ingest.get_vectorstore", return_value=mock_vs_instance):
        with patch("app.api.endpoints.ingest.save_vectorstore"):
            with patch("app.api.endpoints.ingest.get_embeddings"):
                # Use dependency overrides
                app.dependency_overrides[get_db] = lambda: mock_db
                
                try:
                    response = client.post(
                        "/ingest",
                        json={"text": "Hello world", "filename": "test.txt"}
                    )
                    
                    if response.status_code != 200:
                        print(response.json())
                        
                    assert response.status_code == 200
                    assert response.json() == {"status": "success", "message": "Document ingested successfully"}
                    
                    # Verify FAISS was called
                    mock_vs_instance.add_documents.assert_called_once()
                    
                    # Verify DB was called
                    mock_db.add.assert_called_once()
                    mock_db.commit.assert_called_once()
                finally:
                    app.dependency_overrides.clear()
