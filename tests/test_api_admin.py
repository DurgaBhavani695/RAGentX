from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_config():
    response = client.get("/admin/config")
    assert response.status_code == 200
    data = response.json()
    assert "PROJECT_NAME" in data
    assert data["PROJECT_NAME"] == "RAGentX"

def test_put_config_success():
    # Update PROJECT_NAME
    response = client.put("/admin/config/PROJECT_NAME", json="NewProjectName")
    assert response.status_code == 200
    assert response.json() == {"PROJECT_NAME": "NewProjectName"}
    
    # Verify change
    response = client.get("/admin/config")
    assert response.json()["PROJECT_NAME"] == "NewProjectName"

def test_put_config_invalid_key():
    response = client.put("/admin/config/NON_EXISTENT_KEY", json="Value")
    assert response.status_code == 404
    assert response.json()["detail"] == "Configuration key 'NON_EXISTENT_KEY' not found"
