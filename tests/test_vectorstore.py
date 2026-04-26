import os
import shutil
import pytest
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from app.retrieval.vectorstore import get_vectorstore, save_vectorstore
from app.core.config import settings

@pytest.fixture
def clean_vectorstore():
    # Setup: remove existing index if any
    if os.path.exists(settings.FAISS_INDEX_PATH):
        shutil.rmtree(os.path.dirname(settings.FAISS_INDEX_PATH), ignore_errors=True)
    yield
    # Teardown: cleanup
    if os.path.exists(settings.FAISS_INDEX_PATH):
         shutil.rmtree(os.path.dirname(settings.FAISS_INDEX_PATH), ignore_errors=True)

def test_get_vectorstore_new(clean_vectorstore):
    embeddings = FakeEmbeddings(size=1536)
    vectorstore = get_vectorstore(embeddings)
    assert isinstance(vectorstore, FAISS)
    # New vectorstore should be empty or at least initialized
    assert vectorstore.index.ntotal == 0

def test_save_and_load_vectorstore(clean_vectorstore):
    embeddings = FakeEmbeddings(size=1536)
    vectorstore = get_vectorstore(embeddings)
    vectorstore.add_texts(["Hello world"])
    
    save_vectorstore(vectorstore)
    
    # Check if files exist
    assert os.path.exists(settings.FAISS_INDEX_PATH)
    
    # Load it back
    loaded_vs = get_vectorstore(embeddings)
    assert loaded_vs.index.ntotal == 1
