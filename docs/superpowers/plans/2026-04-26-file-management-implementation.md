# File Upload & Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement file upload, document management, configurable limits, and web search fallback.

**Architecture:** Use FastAPI for backend file processing and metadata management. Store files locally and metadata in SQLite. Integrate DuckDuckGo/Tavily for web search fallback in the LangGraph agent.

**Tech Stack:** FastAPI, Streamlit, SQLAlchemy, LangChain, FAISS, DuckDuckGo-Search.

---

### Task 1: Database Schema Updates

**Files:**
- Modify: `app/database/models.py`

- [ ] **Step 1: Add AppConfig model and update DocMetadata**

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
# ... existing imports

class AppConfig(Base):
    __tablename__ = "app_config"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)

# Update DocMetadata to include file info
class DocMetadata(Base):
    __tablename__ = "doc_metadata"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    page_number = Column(Integer)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    extra_info = Column(JSON)
```

- [ ] **Step 2: Commit**

```bash
git add app/database/models.py
git commit -m "db: add AppConfig and update DocMetadata schema"
```

### Task 2: System Initialization and Reset Scripts

**Files:**
- Create: `scripts/init_db.py`
- Create: `scripts/reset_system.py`

- [ ] **Step 1: Create initialization script**

```python
import sys
import os
sys.path.append(os.getcwd())
from app.database.session import engine, SessionLocal
from app.database.models import Base, AppConfig

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Default configs
    defaults = [
        {"key": "max_file_size_mb", "value": 5},
        {"key": "max_files_per_upload", "value": 5},
        {"key": "max_total_files", "value": 10}
    ]
    for d in defaults:
        if not db.query(AppConfig).filter(AppConfig.key == d["key"]).first():
            db.add(AppConfig(**d))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
```

- [ ] **Step 2: Create reset script**

```python
import os
import shutil
import sys
sys.path.append(os.getcwd())
from app.database.session import engine, SessionLocal
from app.database.models import Base
from scripts.init_db import init_db

def reset_system():
    # 1. Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # 2. Clear uploads directory
    upload_dir = "data/uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 3. Clear vectorstore
    vector_dir = "vectorstore"
    if os.path.exists(vector_dir):
        shutil.rmtree(vector_dir)
    
    # 4. Re-init
    init_db()
    print("System reset complete.")

if __name__ == "__main__":
    reset_system()
```

- [ ] **Step 3: Commit**

```bash
git add scripts/init_db.py scripts/reset_system.py
git commit -m "feat: add init and reset scripts"
```

### Task 3: Admin Configuration APIs

**Files:**
- Create: `app/api/endpoints/admin.py`
- Modify: `app/main.py`

- [ ] **Step 1: Implement Admin endpoints**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import AppConfig
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class ConfigUpdate(BaseModel):
    value: Any

@router.get("/config")
def get_all_config(db: Session = Depends(get_db)):
    configs = db.query(AppConfig).all()
    return {c.key: c.value for c in configs}

@router.put("/config/{key}")
def update_config(key: str, update: ConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(AppConfig).filter(AppConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config key not found")
    config.value = update.value
    db.commit()
    return {"status": "success", "key": key, "value": update.value}
```

- [ ] **Step 2: Register admin router in main.py**

```python
# app/main.py
from app.api.endpoints import chat, ingest, admin
# ...
app.include_router(admin.router, prefix="/admin", tags=["admin"])
```

- [ ] **Step 3: Commit**

```bash
git add app/api/endpoints/admin.py app/main.py
git commit -m "feat: add admin config APIs"
```

### Task 4: File Upload & Ingestion Logic

**Files:**
- Modify: `app/retrieval/document_loaders.py`
- Modify: `app/api/endpoints/ingest.py`

- [ ] **Step 1: Enhance document loaders**

```python
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os

def load_file_to_documents(file_path: str, metadata: dict):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    docs = loader.load()
    for doc in docs:
        doc.metadata.update(metadata)
    return docs
```

- [ ] **Step 2: Implement File Upload and Management endpoints**

```python
from fastapi import UploadFile, File, Form
from typing import List
import shutil
import os

# Update ingest.py to add:
# POST /ingest/file
# GET /documents
# GET /documents/{doc_id}/download
# DELETE /documents/{doc_id}

# Need to implement validation logic using AppConfig
```

- [ ] **Step 3: Commit**

```bash
git add app/retrieval/document_loaders.py app/api/endpoints/ingest.py
git commit -m "feat: implement file upload and management APIs"
```

### Task 5: Web Search Tool Integration

**Files:**
- Modify: `app/agents/nodes/retriever.py`
- Modify: `app/agents/graph.py`
- Modify: `app/agents/state.py`

- [ ] **Step 1: Update State to include web search flag**

- [ ] **Step 2: Add DuckDuckGo tool to agent**

- [ ] **Step 3: Update Retriever node to fallback to web search if enabled**

- [ ] **Step 4: Commit**

```bash
git add app/agents/nodes/retriever.py app/agents/graph.py app/agents/state.py
git commit -m "feat: integrate web search tool"
```

### Task 6: Frontend Enhancements

**Files:**
- Modify: `frontend/app.py`

- [ ] **Step 1: Add Web Search toggle in sidebar**

- [ ] **Step 2: Add Document Management tab with table and actions**

- [ ] **Step 3: Update Chat interface to send web search flag**

- [ ] **Step 4: Commit**

```bash
git add frontend/app.py
git commit -m "feat: update frontend with file management and web search"
```
