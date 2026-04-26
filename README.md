# RAGentX: Agentic Retrieval-Augmented Generation System

A production-ready Agentic RAG system orchestrated by **LangGraph**, utilizing **FastAPI** for the backend, **FAISS** and **BM25** for hybrid retrieval, and **Groq-hosted Llama 3** for intelligent multi-agent reasoning.

## 🚀 Key Features

- **Multi-Agent Orchestration**: A sophisticated pipeline involving specialized agents:
  - **Rewriter**: Contextualizes user queries based on conversation history.
  - **Retriever**: Performs hybrid search (Semantic + Keyword).
  - **Evaluator**: Grades document relevance to ensure quality context.
  - **Generator**: Produces high-fidelity responses with source attribution.
  - **Validator**: Checks for hallucinations and ensures response integrity.
- **Agentic Self-Correction**: Implements a conditional retry loop. If retrieved documents are irrelevant, the system automatically re-attempts query rewriting and retrieval (up to 3 times) before responding.
- **Hybrid Search**: Combines **FAISS** (dense vector matching) with **BM25** (sparse keyword matching) to maximize recall and precision.
- **Persistent Memory**: Uses **SQLAlchemy** and **SQLite** to persist chat history across sessions, enabling long-term contextual awareness.
- **Transparent Traceability**: Built-in "Debug Mode" exposes the internal agent reasoning trace (rewritten queries, relevance scores, retry counts) for full auditability.
- **Streamlit UI**: A modern, interactive frontend for document ingestion and real-time chat testing.

## 🛠️ Tech Stack

- **Framework**: LangChain & LangGraph
- **API**: FastAPI
- **LLM**: Groq (Llama 3-8b-8192) via OpenAI-compatible endpoint
- **Vector Store**: FAISS
- **Database**: SQLite (SQLAlchemy ORM)
- **UI**: Streamlit

## 📂 Project Structure

```text
app/
├── api/             # FastAPI routers and endpoints
├── agents/          # LangGraph state, graph, and node logic
├── retrieval/       # Hybrid search and vectorstore management
├── database/        # SQLite models and session management
├── core/            # App configuration and logging
frontend/            # Streamlit UI
```

## 🏃 Quick Start

### 1. Prerequisites
- Python 3.10+
- Groq API Key
- OpenAI API Key (for Embeddings)

### 2. Installation
```bash
git clone https://github.com/DurgaBhavani695/RAGentX.git
cd RAGentX
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root:
```text
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=sqlite:///./ragentx.db
FAISS_INDEX_PATH=vectorstore/faiss_index
```

### 4. Run the Backend (FastAPI)
```bash
python -m uvicorn app.main:app --reload
```

### 5. Run the Frontend (Streamlit)
```bash
streamlit run frontend/app.py
```

## 📄 License
MIT
