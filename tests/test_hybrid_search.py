from langchain_core.documents import Document
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from app.retrieval.hybrid_search import create_hybrid_retriever

def test_create_hybrid_retriever():
    documents = [
        Document(page_content="The cat is on the mat", metadata={"id": 1}),
        Document(page_content="Dogs are friendly animals", metadata={"id": 2}),
        Document(page_content="The quick brown fox jumps over the lazy dog", metadata={"id": 3}),
    ]
    
    embeddings = FakeEmbeddings(size=1536)
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    retriever = create_hybrid_retriever(documents, vectorstore)
    
    # Test semantic search (FAISS)
    # "fox" is in doc 3. Semantic search should find it.
    results = retriever.invoke("fox")
    assert len(results) > 0
    assert any("fox" in doc.page_content for doc in results)

    # Test keyword search (BM25)
    # "friendly" is in doc 2. BM25 should find it.
    results = retriever.invoke("friendly")
    assert len(results) > 0
    assert any("friendly" in doc.page_content for doc in results)
