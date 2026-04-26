# GEMINI.md - Project Context

This file provides instructional context for Gemini CLI interactions within the `RAGentX` project.

## Project Overview

**Project Name:** RAGentX
**Type:** Agentic RAG System
**Primary Technology:** Python (>= 3.10), uv, FastAPI, LangChain, LangGraph, FAISS, BM25, Groq, Streamlit.

RAGentX is a sophisticated multi-agent system designed for high-precision retrieval and reasoning. It features a self-correcting agentic loop that improves retrieval accuracy through iterative evaluation and query refinement.

## Architecture

- **Backend (`app/`)**: FastAPI application.
    - `api/`: REST endpoints (Chat, Ingest).
    - `agents/`: Multi-agent orchestration via LangGraph nodes and state.
    - `retrieval/`: Hybrid search engine (FAISS + BM25).
    - `database/`: Persistence layer for history and metadata (SQLite).
    - `services/`: Global services including the `llm_factory`.
    - `core/`: Configuration and logging.
- **Frontend (`frontend/`)**: Streamlit dashboard.
    - `app.py`: Interactive chat and ingestion UI.
- **Data (`sample_data/`)**: High-quality markdown documents for testing.

## Building and Running

### Fast Setup (Recommended)
The project includes a one-click initialization script for Windows:
```bash
./setup.bat
```

### Integrated Execution
To launch both the backend and frontend concurrently:
```bash
uv run python init_and_run.py
```

### Environment Setup
1. Create a `.env` file from the instructions in `README.md`.
2. Add your `GROQ_API_KEY`.
3. Install dependencies:
   ```bash
   uv sync
   ```

## Development Conventions

- **TDD**: Always maintain and update tests in `tests/` for new features.
- **LLM Factory**: Use `app.services.llm_factory.get_llm()` to instantiate models.
- **Agentic Loops**: Use LangGraph `StateGraph` for all agentic workflows.
- **Hybrid Retrieval**: Ensure both vector (FAISS) and keyword (BM25) search are utilized.
