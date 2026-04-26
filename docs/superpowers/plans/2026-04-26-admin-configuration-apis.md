# Task 3: Admin Configuration APIs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement admin endpoints to GET and PUT system configurations.

**Architecture:** Create a new FastAPI router for admin tasks, register it in `app/main.py`, and implement logic to interact with the global `settings` object.

**Tech Stack:** FastAPI, Pydantic, pytest.

---

### Task 1: Setup Admin Tests

**Files:**
- Create: `tests/test_api_admin.py`

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_api_admin.py`
Expected: FAIL (404 Not Found because routes don't exist yet)

---

### Task 2: Implement Admin Endpoints

**Files:**
- Create: `app/api/endpoints/admin.py`

- [ ] **Step 1: Write minimal implementation**

```python
from fastapi import APIRouter, HTTPException, Body
from app.core.config import settings

router = APIRouter()

@router.get("/config")
async def get_config():
    return settings.model_dump()

@router.put("/config/{key}")
async def update_config(key: str, value: str = Body(...)):
    if not hasattr(settings, key):
        raise HTTPException(status_code=404, detail=f"Configuration key '{key}' not found")
    
    setattr(settings, key, value)
    return {key: getattr(settings, key)}
```

- [ ] **Step 2: Register router in app/main.py**

Modify `app/main.py`:
```python
from app.api.endpoints import ingest, chat, admin  # Add admin

# ... existing code ...

app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])  # Add this
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_api_admin.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_api_admin.py app/api/endpoints/admin.py app/main.py
git commit -m "feat: add admin config APIs"
```
