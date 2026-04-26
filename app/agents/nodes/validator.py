import logging
from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.services.llm_factory import get_llm

logger = logging.getLogger(__name__)

def validate_generation(state: AgentState):
    """
    Validates the generated answer (e.g., for hallucinations or safety).
    """
    logger.info("Validating generated answer...")
    llm = get_llm()

    query = state.get("rewritten_query") or state["query"]
    generation = state.get("generation", "")
    retrieved_docs = state.get("retrieved_docs", [])
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict validator. Check if the AI's answer is fully supported by the provided context and does not contain hallucinations. Respond with exactly one word: 'valid' if the answer is accurate and grounded, or 'invalid' if it is unsupported or incorrect. Do not provide any explanation."),
        ("human", "Context:\n{context}\n\nQuestion: {query}\nProposed Answer: {generation}")
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

    logger.info(f"Validation result: {status}")
    debug_info = state.get("debug_info", {}).copy()
    debug_info["validator_status"] = status
    
    return {
        "debug_info": debug_info
    }
