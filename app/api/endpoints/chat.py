from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database.session import get_db
from app.database.models import ChatHistory
from app.agents.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    debug_info: Optional[dict] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, debug: bool = Query(False), db: Session = Depends(get_db)):
    try:
        # 1. Load chat history from DB
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
            "debug_info": {}
        }
        
        final_state = graph.invoke(initial_state)

        # 3. Save to DB
        user_msg = ChatHistory(session_id=request.session_id, role="user", content=request.query)
        ai_msg = ChatHistory(session_id=request.session_id, role="assistant", content=final_state["generation"])
        
        db.add(user_msg)
        db.add(ai_msg)
        db.commit()

        # 4. Prepare response
        return ChatResponse(
            response=final_state["generation"],
            session_id=request.session_id,
            debug_info=final_state.get("debug_info") if debug else None
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
