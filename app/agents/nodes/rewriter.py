from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents.state import AgentState
from app.core.config import settings

def rewrite_query(state: AgentState):
    """
    Rewrites the user's query to be a standalone query based on the chat history.
    """
    llm = ChatOpenAI(
        base_url=settings.GROQ_API_BASE,
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the following chat history and a follow up question, rephrase the follow up question to be a standalone question that can be understood without the chat history. If it is already a standalone question, return it as is."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{query}")
    ])    
    chain = prompt | llm
    
    response = chain.invoke({
        "chat_history": state["chat_history"],
        "query": state["query"]
    })
    
    rewritten_query = response.content
    
    # Update debug info
    debug_info = state.get("debug_info", {}).copy()
    debug_info["rewriter"] = rewritten_query
    
    return {
        "rewritten_query": rewritten_query,
        "debug_info": debug_info
    }
