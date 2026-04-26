from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm():
    """
    Returns a configured ChatOpenAI instance pointing to Groq.
    """
    return ChatOpenAI(
        base_url=settings.GROQ_API_BASE,
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0
    )
