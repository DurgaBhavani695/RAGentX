from app.agents.state import AgentState
from app.retrieval.hybrid_search import create_hybrid_retriever
from app.retrieval.vectorstore import get_vectorstore
from langchain_openai import OpenAIEmbeddings

def retrieve_docs(state: AgentState):
    """
    Retrieves documents using hybrid search based on the rewritten query.
    """
    rewritten_query = state.get("rewritten_query") or state["query"]
    
    # In a real app, you'd likely load documents from a DB or pre-indexed vectorstore
    # For now, we'll assume the vectorstore is already populated or we load it
    embeddings = OpenAIEmbeddings()
    vectorstore = get_vectorstore(embeddings)
    
    # Since BM25 needs the list of documents, and FAISS has them indexed,
    # in a production scenario you might fetch all docs from FAISS or a DB for BM25.
    # For this implementation, we'll try to get the retriever.
    # Note: If no docs are provided to create_hybrid_retriever, it falls back to FAISS only.
    retriever = create_hybrid_retriever([], vectorstore)
    
    docs = retriever.invoke(rewritten_query)
    
    debug_info = state.get("debug_info", {}).copy()
    debug_info["retrieved_docs_count"] = len(docs)
    
    return {
        "retrieved_docs": docs,
        "debug_info": debug_info
    }
