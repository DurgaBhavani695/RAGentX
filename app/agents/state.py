from typing import TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class AgentState(TypedDict):
    query: str
    rewritten_query: str
    chat_history: list[BaseMessage]
    retrieved_docs: list[Document]
    generation: str
    retry_count: int
    debug_info: dict
    use_web_search: bool
