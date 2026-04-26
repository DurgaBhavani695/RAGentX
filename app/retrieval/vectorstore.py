import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

logger = logging.getLogger(__name__)
_embeddings = None

def get_embeddings() -> Embeddings:
    """
    Returns the configured embedding model (defaults to free local HuggingFace model).
    Caches the instance to avoid reloading the model on every call.
    """
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
        _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully.")
    return _embeddings

def get_vectorstore(embeddings: Embeddings) -> FAISS:
    """
    Load an existing FAISS index from disk or create a new empty one.
    """
    index_path = settings.FAISS_INDEX_PATH
    
    if os.path.exists(index_path):
        logger.info(f"Loading existing FAISS index from {index_path}...")
        return FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        logger.info("No existing FAISS index found. Initializing empty index...")
        # Create an empty FAISS index by initializing with one text and then deleting it.
        vectorstore = FAISS.from_texts(["initialization"], embeddings)
        vectorstore.delete([vectorstore.index_to_docstore_id[0]])
        logger.info("Empty FAISS index initialized.")
        return vectorstore

def save_vectorstore(vectorstore: FAISS):
    """
    Save the FAISS index to the configured path.
    """
    index_path = settings.FAISS_INDEX_PATH
    logger.info(f"Saving FAISS index to {index_path}...")
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    vectorstore.save_local(index_path)
    logger.info("FAISS index saved successfully.")
