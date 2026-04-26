import os
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

def get_embeddings() -> Embeddings:
    """
    Returns the configured embedding model (defaults to free local HuggingFace model).
    """
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

def get_vectorstore(embeddings: Embeddings) -> FAISS:
    """
    Load an existing FAISS index from disk or create a new empty one.
    """
    index_path = settings.FAISS_INDEX_PATH
    
    if os.path.exists(index_path):
        return FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        # Create an empty FAISS index by initializing with one text and then deleting it.
        # This ensures the index has the correct dimension from the embeddings.
        vectorstore = FAISS.from_texts(["initialization"], embeddings)
        # Delete the initialization text
        vectorstore.delete([vectorstore.index_to_docstore_id[0]])
        return vectorstore

def save_vectorstore(vectorstore: FAISS):
    """
    Save the FAISS index to the configured path.
    """
    index_path = settings.FAISS_INDEX_PATH
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    vectorstore.save_local(index_path)
