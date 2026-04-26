from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAGentX"
    DATABASE_URL: str = "sqlite:///./ragentx.db"
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: str
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"
    FAISS_INDEX_PATH: str = "vectorstore/faiss_index"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
