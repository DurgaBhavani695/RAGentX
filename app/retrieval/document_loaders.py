from typing import List, Dict, Any
from langchain_core.documents import Document

def text_to_documents(text: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """
    Converts raw text into a list containing a single LangChain Document object.
    In a real scenario, this might involve splitting text into chunks.
    """
    return [Document(page_content=text, metadata=metadata or {})]
