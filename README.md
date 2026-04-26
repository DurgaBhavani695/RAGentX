# RAGentX 🤖
**The Self-Correcting Multi-Agent RAG Orchestrator**

RAGentX is a production-grade **Agentic Retrieval-Augmented Generation (RAG)** system designed to bridge the gap between static documents and actionable intelligence. Unlike standard "one-shot" RAG systems, RAGentX uses **Agentic Loops** powered by **LangGraph** to architect, retrieve, evaluate, and self-correct its own reasoning path.

---

## ✨ Key Features

### 🧠 Intelligent Orchestration (DAG)
RAGentX uses a stateful **Directed Acyclic Graph (DAG)** to manage the entire retrieval lifecycle.

```mermaid
graph TD
    %% Entry Point
    START((START)) --> Rewriter[Query Rewriter]

    %% Main Pipeline
    subgraph "Agentic Pipeline"
        Rewriter --> Retriever[Hybrid Retriever]
        Retriever --> Evaluator[Context Evaluator]
    end

    %% Self-Correction Logic
    Evaluator -->|Relevant| Generator[Response Generator]
    Evaluator -->|"Irrelevant (Retry < 3)"| Rewriter
    Evaluator -->|Fallback| Generator

    %% Validation Gate
    Generator --> Validator[Output Validator]
    Validator -->|Valid| END((END))
    Validator -->|Invalid| Generator

    %% Visual Styles
    style START fill:#0f172a,stroke:#38bdf8,color:#fff
    style END fill:#0f172a,stroke:#38bdf8,color:#fff
    classDef agentNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    class Rewriter,Retriever,Evaluator,Generator,Validator agentNode
```

- **Agentic Self-Correction**: Implements a recursive "Reflexion" loop. If the agent determines the retrieved data is irrelevant, it autonomously rewrites the query and tries again.
- **Hybrid Ensemble Retrieval**: Combines **FAISS** (dense vector search) with **BM25** (keyword search) to ensure both semantic breadth and keyword precision.
- **Free Local Embeddings**: Optimized for performance and cost by using local **HuggingFace** models (`all-MiniLM-L6-v2`) for vectorization.
- **High-Speed Generation**: Powered by **Groq Llama 3.3**, delivering enterprise-grade reasoning at lightning speeds.

### 🛠️ Developer Experience (DX)
- **Unified Entry Point**: Launch the full stack (FastAPI + Streamlit) with a single command: `uv run python init_and_run.py`.
- **Transparent Traceability**: Built-in "Debug Mode" allows developers to inspect the agent's internal trace, including rewritten queries and relevance scores.
- **Robust Persistence**: Uses **SQLAlchemy** to manage session-based chat history and document metadata.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Modern Python package manager)
- Groq API Key

### 2. Initialization & Setup
Run the automated setup script:
```bash
# Windows
./setup.bat
```
Or manually:
```bash
uv sync
```

### 3. Configuration
Add your keys to the generated `.env` file:
```env
GROQ_API_KEY=your_groq_key_here
GROQ_API_BASE=https://api.groq.com/openai/v1
GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

### 4. Run Everything
```bash
uv run python init_and_run.py
```

---

## 📂 Project Structure
```text
app/
├── api/             # FastAPI REST endpoints
├── agents/          # LangGraph nodes and orchestration
├── retrieval/       # Hybrid search and vectorstore logic
├── services/        # Centralized LLM factory
├── database/        # SQLite models and session management
frontend/            # Streamlit interactive dashboard
sample_data/         # Professional test documents
```

---

## 📋 Resume-Ready Technical Stack
- **AI Framework**: LangChain & LangGraph
- **LLM Engine**: Groq (Llama 3.3) via OpenAI API
- **Vector Store**: FAISS
- **Retrieval**: Hybrid (Dense + Sparse)
- **API**: FastAPI
- **Frontend**: Streamlit
- **Package Manager**: uv

---

## 📄 License
MIT
