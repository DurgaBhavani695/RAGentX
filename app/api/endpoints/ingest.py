from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
import shutil
from datetime import datetime, timezone
import logging

from app.database.session import get_db
from app.database.models import DocMetadata, AppConfig
from app.retrieval.vectorstore import get_vectorstore, save_vectorstore, get_embeddings
from app.retrieval.document_loaders import text_to_documents, load_file_to_documents

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = logging.getLogger(__name__)

class IngestRequest(BaseModel):
    text: str
    filename: Optional[str] = None

@router.post("")
@router.post("/")
async def ingest_text(request: IngestRequest, db: Session = Depends(get_db)):
    try:
        doc_id = str(uuid.uuid4())
        metadata = {"doc_id": doc_id, "filename": request.filename}
        docs = text_to_documents(request.text, metadata=metadata)

        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        vectorstore.add_documents(docs)
        save_vectorstore(vectorstore)
        
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
        logger.exception("Error in ingest_text")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def ingest_file(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        # 1. Query AppConfig for limits
        configs = db.query(AppConfig).all()
        config_dict = {c.key: c.value for c in configs}
        
        max_file_size_mb = config_dict.get("max_file_size_mb", 5)
        max_files_per_upload = config_dict.get("max_files_per_upload", 5)
        max_total_files = config_dict.get("max_total_files", 10)
        
        if len(files) > max_files_per_upload:
            raise HTTPException(status_code=400, detail=f"Too many files. Max {max_files_per_upload} per upload.")
        
        total_existing = db.query(DocMetadata).count()
        if total_existing + len(files) > max_total_files:
            raise HTTPException(status_code=400, detail=f"Total limit reached. Max {max_total_files} total files.")
        
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        ingested_files = []
        
        # Load embeddings once for all files
        logger.info("Accessing embeddings...")
        embeddings = get_embeddings()
        
        for file in files:
            # Check size
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > max_file_size_mb * 1024 * 1024:
                logger.warning(f"File {file.filename} exceeds size limit: {file_size} bytes")
                continue # Skip this file but continue with others
            
            doc_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, f"{doc_id}_{file.filename}")
            
            logger.info(f"Processing {file.filename} (ID: {doc_id})...")
            
            # Save file locally
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Load and chunk documents
            metadata = {
                "doc_id": doc_id,
                "filename": file.filename,
                "file_path": file_path,
                "file_size": file_size
            }
            
            try:
                docs = load_file_to_documents(file_path, metadata=metadata)
                if not docs:
                    logger.warning(f"No text extracted from {file.filename}")
                    continue

                # Add to FAISS and save immediately to avoid keeping it in memory
                # Load vectorstore fresh each time to avoid state issues during multi-file upload
                vectorstore = get_vectorstore(embeddings)
                
                # Add in smaller batches if many docs
                batch_size = 50
                for i in range(0, len(docs), batch_size):
                    batch = docs[i : i + batch_size]
                    vectorstore.add_documents(batch)
                
                save_vectorstore(vectorstore)
                
                # Save to DB
                db_doc = DocMetadata(
                    doc_id=doc_id,
                    filename=file.filename,
                    file_path=file_path,
                    file_size=file_size,
                    upload_date=datetime.now(timezone.utc)
                )
                db.add(db_doc)
                db.commit()
                
                ingested_files.append({"doc_id": doc_id, "filename": file.filename})
                logger.info(f"Successfully ingested {file.filename}")
                
            except Exception as e:
                logger.exception(f"Failed to process file {file.filename}")
                # Cleanup partially saved file if it failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                continue

        return {"status": "success", "data": ingested_files}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Global error in ingest_file")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    try:
        docs = db.query(DocMetadata).all()
        return docs
    except Exception as e:
        logger.exception("Error listing documents")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocMetadata).filter(DocMetadata.doc_id == doc_id).first()
    if not doc or not doc.file_path:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(doc.file_path):
         raise HTTPException(status_code=404, detail="File missing on disk")
         
    return FileResponse(doc.file_path, filename=doc.filename)

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocMetadata).filter(DocMetadata.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        
        ids_to_delete = []
        for internal_id, document in vectorstore.docstore._dict.items():
            if document.metadata.get("doc_id") == doc_id:
                ids_to_delete.append(internal_id)
        
        if ids_to_delete:
            vectorstore.delete(ids_to_delete)
            save_vectorstore(vectorstore)
            
        db.delete(doc)
        db.commit()
        return {"status": "success", "message": f"Document {doc_id} deleted"}
    except Exception as e:
        logger.exception(f"Error deleting document {doc_id}")
        raise HTTPException(status_code=500, detail=str(e))
