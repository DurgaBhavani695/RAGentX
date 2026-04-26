from app.agents.state import AgentState
from app.retrieval.hybrid_search import create_hybrid_retriever
from app.retrieval.vectorstore import get_vectorstore, get_embeddings
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

def retrieve_docs(state: AgentState):
    """
    Retrieves documents using hybrid search based on the rewritten query.
    Also performs a web search if requested.
    """
    rewritten_query = state.get("rewritten_query") or state["query"]
    
    # Use free local embeddings
    embeddings = get_embeddings()
    vectorstore = get_vectorstore(embeddings)
    
    # Since BM25 needs the list of documents, and FAISS has them indexed,
    # in a production scenario you might fetch all docs from FAISS or a DB for BM25.
    # For this implementation, we'll try to get the retriever.
    # Note: If no docs are provided to create_hybrid_retriever, it falls back to FAISS only.
    retriever = create_hybrid_retriever([], vectorstore)
    
    docs = retriever.invoke(rewritten_query)
    
    # Web search integration
    if state.get("use_web_search"):
        search = DuckDuckGoSearchRun()
        search_results = search.run(rewritten_query)
        web_doc = Document(
            page_content=search_results,
            metadata={"source": "duckduckgo_search", "query": rewritten_query}
        )
        docs.append(web_doc)
    
    debug_info = state.get("debug_info", {}).copy()
    debug_info["retrieved_docs_count"] = len(docs)
    
    return {
        "retrieved_docs": docs,
        "debug_info": debug_info
    }
