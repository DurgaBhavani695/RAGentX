# Agentic RAG System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready Agentic RAG system with FastAPI, LangChain, LangGraph, and FAISS, featuring hybrid search, source attribution, and agentic retry loops.

**Architecture:** A modular domain-driven architecture. LangGraph orchestrates a multi-agent pipeline (Rewriter, Retriever, Evaluator, Generator, Validator) with persistence via SQLAlchemy and hybrid retrieval using FAISS + BM25.

**Tech Stack:** Python 3.10+, FastAPI, LangChain, LangGraph, FAISS-cpu, Rank_BM25, SQLAlchemy, Pydantic.

---

### Task 1: Project Scaffolding & Configuration

**Files:**
- Create: `app/core/config.py`
- Create: `app/core/logger.py`
- Modify: `requirements.txt` (or create if missing)

- [ ] **Step 1: Create requirements.txt**

```text
fastapi
uvicorn
langchain
langchain-community
langchain-openai
langgraph
faiss-cpu
rank_bm25
sqlalchemy
pydantic-settings
python-dotenv
```

- [ ] **Step 2: Implement configuration**

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAGentX"
    DATABASE_URL: str = "sqlite:///./ragentx.db"
    OPENAI_API_KEY: str
    FAISS_INDEX_PATH: str = "vectorstore/faiss_index"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 3: Setup basic logging**

```python
# app/core/logger.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("app")
```

---

### Task 2: Database & Models (Persistence)

**Files:**
- Create: `app/database/models.py`
- Create: `app/database/session.py`

- [ ] **Step 1: Define SQLAlchemy models**

```python
# app/database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DocMetadata(Base):
    __tablename__ = "doc_metadata"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    filename = Column(String)
    page_number = Column(Integer)
    extra_info = Column(JSON)
```

- [ ] **Step 2: Setup database session**

```python
# app/database/session.py
from sqlalchemy import create_all
from sqlalchemy.orm import sessionmaker
from .models import Base, engine # assuming engine setup

# Simplified for plan
```

---

### Task 3: Retrieval Layer (FAISS, BM25, Hybrid Search)

**Files:**
- Create: `app/retrieval/vectorstore.py`
- Create: `app/retrieval/hybrid_search.py`

- [ ] **Step 1: Implement Vectorstore management**

```python
# app/retrieval/vectorstore.py
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def get_vectorstore(embeddings):
    # Load or create FAISS index
    pass
```

- [ ] **Step 2: Implement Hybrid Search**

```python
# app/retrieval/hybrid_search.py
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

def create_hybrid_retriever(documents, vectorstore):
    bm25_retriever = BM25Retriever.from_documents(documents)
    faiss_retriever = vectorstore.as_retriever()
    return EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.3, 0.7]
    )
```

---

### Task 4: Agent State & Nodes

**Files:**
- Create: `app/agents/state.py`
- Create: `app/agents/nodes/rewriter.py`
- Create: `app/agents/nodes/retriever.py`

- [ ] **Step 1: Define Agent State**

```python
# app/agents/state.py
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    query: str
    rewritten_query: str
    chat_history: list[BaseMessage]
    retrieved_docs: list
    generation: str
    retry_count: int
    debug_info: dict
```

- [ ] **Step 2: Implement Rewriter Node**

```python
# app/agents/nodes/rewriter.py
def rewrite_query(state: AgentState):
    # Use LLM to contextualize query based on history
    return {"rewritten_query": "...", "debug_info": {"rewriter": "..."}}
```

---

### Task 5: LangGraph Orchestration

**Files:**
- Create: `app/agents/graph.py`

- [ ] **Step 1: Build the graph**

```python
# app/agents/graph.py
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import rewriter, retriever, evaluator, generator, validator

workflow = StateGraph(AgentState)
workflow.add_node("rewrite", rewriter)
workflow.add_node("retrieve", retriever)
# ... add nodes and edges
workflow.set_entry_point("rewrite")
# ... add conditional edges for retry loop
```

---

### Task 6: FastAPI Endpoints

**Files:**
- Create: `app/api/endpoints/chat.py`
- Create: `app/main.py`

- [ ] **Step 1: Implement Chat Endpoint**

```python
# app/api/endpoints/chat.py
@router.post("/chat")
async def chat(request: ChatRequest, debug: bool = False):
    # Invoke LangGraph
    # Return response + debug_info if requested
    pass
```

- [ ] **Step 2: Setup Main App**

```python
# app/main.py
app = FastAPI()
app.include_router(chat.router)
```

---

### Task 7: End-to-End Validation & Testing

- [ ] **Step 1: Write integration test for retry loop**
- [ ] **Step 2: Verify source attribution in output**
