import os
import pytest
from app.core.config import Settings

def test_settings_load_defaults():
    # Mock keys to allow instantiation
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["GROQ_API_KEY"] = "test-groq-key"
    settings = Settings()
    assert settings.PROJECT_NAME == "RAGentX"
    assert settings.DATABASE_URL == "sqlite:///./ragentx.db"
    assert settings.OPENAI_API_KEY == "test-key"
    assert settings.GROQ_API_KEY == "test-groq-key"
    assert settings.FAISS_INDEX_PATH == "vectorstore/faiss_index"

def test_settings_env_override():
    os.environ["PROJECT_NAME"] = "CustomRAG"
    settings = Settings()
    assert settings.PROJECT_NAME == "CustomRAG"
    # Clean up
    del os.environ["PROJECT_NAME"]
