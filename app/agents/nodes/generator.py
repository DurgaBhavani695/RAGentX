from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.core.config import settings

def generate_answer(state: AgentState):
    """
    Generates an answer based on the retrieved documents and query.
    """
    llm = ChatOpenAI(
        base_url=settings.GROQ_API_BASE,
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0
    )

    retrieved_docs = state.get("retrieved_docs", [])
    query = state.get("rewritten_query") or state["query"]

    # Format context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Answer the user's question using ONLY the provided context. If the answer is not in the context, say you don't know. \n\nContext:\n{context}"),
        ("human", "{query}")
    ])

    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "query": query
    })

    response_text = response.content
    
    if retrieved_docs:
        response_text += "\n\nSources:"
        for i, doc in enumerate(retrieved_docs):
            source = doc.metadata.get("filename", f"Doc {i+1}")
            page = doc.metadata.get("page_number", "N/A")
            response_text += f"\n- {source} (Page {page})"
    
    debug_info = state.get("debug_info", {}).copy()
    debug_info["generator_status"] = "completed"
    debug_info["retrieved_docs_count"] = len(retrieved_docs)
    
    return {
        "generation": response_text,
        "debug_info": debug_info
    }
