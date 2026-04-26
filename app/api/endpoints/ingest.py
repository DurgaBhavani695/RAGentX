from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database.session import get_db
from app.database.models import DocMetadata
from app.retrieval.vectorstore import get_vectorstore, save_vectorstore, get_embeddings
from app.retrieval.document_loaders import text_to_documents

router = APIRouter()

class IngestRequest(BaseModel):
    text: str
    filename: Optional[str] = None

@router.post("/ingest")
async def ingest_text(request: IngestRequest, db: Session = Depends(get_db)):
    try:
        # 1. Convert to Documents
        doc_id = str(uuid.uuid4())
        metadata = {"doc_id": doc_id, "filename": request.filename}
        docs = text_to_documents(request.text, metadata=metadata)

        # 2. Add to FAISS
        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        vectorstore.add_documents(docs)
        save_vectorstore(vectorstore)
        
        # 3. Save to DB
        db_doc = DocMetadata(
            doc_id=doc_id,
            filename=request.filename,
            extra_info={"text_length": len(request.text)}
        )
        db.add(db_doc)
        db.commit()
        
        return {"status": "success", "message": "Document ingested successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
