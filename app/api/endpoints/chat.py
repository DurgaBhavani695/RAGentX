from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging

from app.database.session import get_db
from app.database.models import ChatHistory
from app.agents.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    session_id: str
    query: str
    enable_web_search: bool = False

class ChatResponse(BaseModel):
    response: str
    session_id: str
    debug_info: Optional[dict] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, debug: bool = Query(False), db: Session = Depends(get_db)):
    try:
        logger.info(f"Received chat request for session: {request.session_id}")
        
        # 1. Load chat history from DB
        logger.info("Fetching chat history from database...")
        history_records = db.query(ChatHistory).filter(
            ChatHistory.session_id == request.session_id
        ).order_by(ChatHistory.timestamp.asc()).all()

        chat_history = []
        for rec in history_records:
            if rec.role == "user":
                chat_history.append(HumanMessage(content=rec.content))
            else:
                chat_history.append(AIMessage(content=rec.content))

        # 2. Invoke LangGraph
        initial_state = {
            "query": request.query,
            "chat_history": chat_history,
            "retry_count": 0,
            "use_web_search": request.enable_web_search,
            "debug_info": {}
        }
        
        logger.info("Invoking agentic graph...")
        final_state = graph.invoke(initial_state)
        logger.info("Graph invocation complete.")

        # 3. Save to DB
        logger.info("Saving interaction to chat history...")
        user_msg = ChatHistory(session_id=request.session_id, role="user", content=request.query)
        ai_msg = ChatHistory(session_id=request.session_id, role="assistant", content=final_state["generation"])
        
        db.add(user_msg)
        db.add(ai_msg)
        db.commit()

        # 4. Prepare response
        logger.info("Request processed successfully.")
        return ChatResponse(
            response=final_state["generation"],
            session_id=request.session_id,
            debug_info=final_state.get("debug_info") if debug else None
        )

    except Exception as e:
        db.rollback()
        logger.exception(f"Error in chat endpoint for session {request.session_id}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
