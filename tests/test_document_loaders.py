from langchain_core.documents import Document
from app.retrieval.document_loaders import text_to_documents

def test_text_to_documents():
    text = "Hello world\nThis is a test document."
    metadata = {"source": "test.txt"}
    docs = text_to_documents(text, metadata)
    
    assert len(docs) == 1
    assert docs[0].page_content == text
    assert docs[0].metadata["source"] == "test.txt"
