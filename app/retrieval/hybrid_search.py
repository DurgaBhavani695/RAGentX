from typing import List
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def create_hybrid_retriever(documents: List[Document], vectorstore: FAISS) -> EnsembleRetriever:
    """
    Creates a hybrid retriever combining BM25 and FAISS.
    """
    if not documents:
        # Fallback to just vectorstore if no documents provided for BM25
        return vectorstore.as_retriever()
        
    bm25_retriever = BM25Retriever.from_documents(documents)
    faiss_retriever = vectorstore.as_retriever()
    
    return EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.3, 0.7]
    )
