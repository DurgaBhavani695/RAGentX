from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAGentX"
    DATABASE_URL: str = "sqlite:///./ragentx.db"
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    FAISS_INDEX_PATH: str = "vectorstore/faiss_index"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
