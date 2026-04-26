from langchain_groq import ChatGroq
from app.core.config import settings

def get_llm():
    """
    Factory function to return the configured LLM instance.
    Defaults to Groq Llama 3.3 for high-performance agentic reasoning.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_key_here":
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0,
        max_tokens=4096
    )
