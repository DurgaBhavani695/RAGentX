from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.core.config import settings

def validate_generation(state: AgentState):
    """
    Validates the generated answer (e.g., for hallucinations or safety).
    """
    llm = ChatOpenAI(
        base_url=settings.GROQ_API_BASE,
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0
    )

    query = state.get("rewritten_query") or state["query"]
    generation = state.get("generation", "")
    retrieved_docs = state.get("retrieved_docs", [])
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a validator. Check if the AI's answer is supported by the context and doesn't contain hallucinations. Respond with exactly one word: 'valid' if it is correct, or 'invalid' if it is hallucinated or wrong. \n\nContext:\n{context}"),
        ("human", "Question: {query}\nAnswer: {generation}")
    ])

    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "query": query,
        "generation": generation
    })

    status = response.content.lower().strip()
    if "valid" in status and "invalid" not in status:
        status = "valid"
    else:
        status = "invalid"

    debug_info = state.get("debug_info", {}).copy()
    debug_info["validator_status"] = status
    
    return {
        "debug_info": debug_info
    }
