# RAGentX System Architecture

RAGentX is an enterprise-grade **Agentic Retrieval-Augmented Generation (RAG)** system designed for high-precision information retrieval and multi-step reasoning.

## 🏗️ Core Components

### 1. Multi-Agent Orchestrator (LangGraph)
The system's intelligence is governed by a **Directed Acyclic Graph (DAG)** implemented via LangGraph. This orchestrator manages state transitions and conditional routing between specialized nodes.

### 2. Semantic Retrieval Layer
- **Dense Vector Search**: Powered by **FAISS** and local **HuggingFace** embeddings (`all-MiniLM-L6-v2`).
- **Sparse Keyword Search**: Powered by **BM25** to ensure high precision for specific terminology.
- **Ensemble Retrieval**: A hybrid approach that weights both semantic and keyword scores.

### 3. Agentic Nodes
- **Rewriter**: Re-contextualizes user queries based on session history.
- **Retriever**: Executes the hybrid search against the vector store.
- **Evaluator**: A "Reflexion" node that grades the relevance of retrieved context.
- **Generator**: Produces the final response with cited source attribution.
- **Validator**: Ensures the response is hallucination-free and grounded in the provided facts.

## 🔄 Self-Correction Loop
RAGentX features an autonomous retry loop. If the **Evaluator** determines that retrieved documents are irrelevant, the system triggers a recursive cycle to rewrite the query and re-attempt retrieval (up to a limit of 3 attempts), ensuring the model never answers based on poor data.

## 💾 Persistence & Memory
The system uses **SQLAlchemy** with a **SQLite** backend to maintain long-term chat history and document metadata, enabling coherent multi-turn conversations.
