from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os

def text_to_documents(text: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Converts raw text into a list containing a single LangChain Document object.
    In a real scenario, this might involve splitting text into chunks.
    """
    return [Document(page_content=text, metadata=metadata or {})]

def load_file_to_documents(file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Loads a file (PDF, TXT, MD) and converts it into a list of LangChain Document objects.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    else:
        # Default to TextLoader for .txt, .md, etc.
        loader = TextLoader(file_path, encoding="utf-8")
    
    docs = loader.load()
    if metadata:
        for doc in docs:
            doc.metadata.update(metadata)
    return docs
