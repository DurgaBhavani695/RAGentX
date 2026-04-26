from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.services.llm_factory import get_llm

def generate_answer(state: AgentState):
    """
    Generates an answer based on the retrieved documents and query.
    """
    llm = get_llm()

    retrieved_docs = state.get("retrieved_docs", [])
    query = state.get("rewritten_query") or state["query"]

    # Format context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly capable AI assistant. Answer the user's question using ONLY the provided context. If the answer is not contained in the context, explicitly state that you don't know based on the provided documents. Maintain a professional tone.\n\nContext:\n{context}"),
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
        # Use a set to avoid duplicate sources
        sources = set()
        for doc in retrieved_docs:
            source_name = doc.metadata.get("filename", "Unknown")
            page_num = doc.metadata.get("page_number", "N/A")
            sources.add(f"- {source_name} (Page {page_num})")
        
        response_text += "\n" + "\n".join(sorted(list(sources)))
    
    debug_info = state.get("debug_info", {}).copy()
    debug_info["generator_status"] = "completed"
    debug_info["retrieved_docs_count"] = len(retrieved_docs)
    
    return {
        "generation": response_text,
        "debug_info": debug_info
    }
