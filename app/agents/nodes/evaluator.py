from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.services.llm_factory import get_llm

def evaluate_docs(state: AgentState):
    """
    Evaluates the relevance of retrieved documents to the query.
    """
    llm = get_llm()

    query = state.get("rewritten_query") or state["query"]
    retrieved_docs = state.get("retrieved_docs", [])
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert evaluator. Grade the relevance of the retrieved documents to the user's question. Respond with exactly one word: 'relevant' if at least one document is useful, or 'irrelevant' if none are useful. Do not provide any explanation."),
        ("human", "Context:\n{context}\n\nQuestion: {query}")
    ])

    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "query": query
    })

    relevance = response.content.lower().strip()
    # Normalize
    if "relevant" in relevance and "irrelevant" not in relevance:
        relevance = "relevant"
    else:
        relevance = "irrelevant"

    debug_info = state.get("debug_info", {}).copy()
    debug_info["evaluator_relevance"] = relevance
    
    retry_count = state.get("retry_count", 0)
    if relevance == "irrelevant":
        retry_count += 1
    
    return {
        "debug_info": debug_info,
        "retry_count": retry_count
    }
