from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os

def text_to_documents(text: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Converts raw text into a list of LangChain Document objects.
    Chunks the text to ensure chunks are small enough for embeddings.
    """
    doc = Document(page_content=text, metadata=metadata or {})
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    return text_splitter.split_documents([doc])

from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_file_to_documents(file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Loads a file (PDF, TXT, MD) and converts it into a list of LangChain Document objects.
    Chunks the documents to ensure they are small enough for embeddings.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    else:
        # Default to TextLoader for .txt, .md, etc.
        loader = TextLoader(file_path, encoding="utf-8")
    
    docs = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    split_docs = text_splitter.split_documents(docs)
    
    if metadata:
        for doc in split_docs:
            doc.metadata.update(metadata)
    return split_docs
