from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
import shutil
from datetime import datetime, timezone

from app.database.session import get_db
from app.database.models import DocMetadata, AppConfig
from app.retrieval.vectorstore import get_vectorstore, save_vectorstore, get_embeddings
from app.retrieval.document_loaders import text_to_documents, load_file_to_documents

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestRequest(BaseModel):
    text: str
    filename: Optional[str] = None

@router.post("")
@router.post("/")
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

import logging

logger = logging.getLogger(__name__)

@router.post("/file")
async def ingest_file(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        # 1. Query AppConfig for limits
        configs = db.query(AppConfig).all()
        config_dict = {c.key: c.value for c in configs}
        
        max_file_size_mb = config_dict.get("max_file_size_mb", 5)
        max_files_per_upload = config_dict.get("max_files_per_upload", 5)
        max_total_files = config_dict.get("max_total_files", 10)
        
        # 2. Validate number of files
        if len(files) > max_files_per_upload:
            raise HTTPException(status_code=400, detail=f"Too many files. Max {max_files_per_upload} per upload.")
        
        # 3. Check total existing files
        total_existing = db.query(DocMetadata).count()
        if total_existing + len(files) > max_total_files:
            raise HTTPException(status_code=400, detail=f"Total limit reached. Max {max_total_files} total files.")
        
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        ingested_files = []
        
        logger.info("Initializing embeddings and vectorstore...")
        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        
        for file in files:
            # 4. Check size
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > max_file_size_mb * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds {max_file_size_mb}MB limit.")
            
            # 5. Save to disk
            doc_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, f"{doc_id}_{file.filename}")
            
            logger.info(f"Saving file {file.filename} to {file_path}")
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # 6. Load docs
            metadata = {
                "doc_id": doc_id,
                "filename": file.filename,
                "file_path": file_path,
                "file_size": file_size
            }
            logger.info(f"Parsing file {file.filename}...")
            docs = load_file_to_documents(file_path, metadata=metadata)
            
            # 7. Add to FAISS
            if docs:
                logger.info(f"Adding {len(docs)} chunks to FAISS...")
                vectorstore.add_documents(docs)
            
            # 8. Save Metadata to DB
            db_doc = DocMetadata(
                doc_id=doc_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                upload_date=datetime.now(timezone.utc)
            )
            db.add(db_doc)
            ingested_files.append({"doc_id": doc_id, "filename": file.filename})
        
        db.commit()
        logger.info("Saving vectorstore...")
        save_vectorstore(vectorstore)
        
        return {"status": "success", "data": ingested_files}
    except HTTPException as e:
        db.rollback()
        logger.error(f"HTTP Error during ingestion: {e.detail}")
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error during file ingestion")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(DocMetadata).all()
    return docs

@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocMetadata).filter(DocMetadata.doc_id == doc_id).first()
    if not doc or not doc.file_path:
        raise HTTPException(status_code=404, detail="Document not found on disk")
    
    if not os.path.exists(doc.file_path):
         raise HTTPException(status_code=404, detail="File not found on disk")
         
    return FileResponse(doc.file_path, filename=doc.filename)

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocMetadata).filter(DocMetadata.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 1. Delete from Disk
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    # 2. Delete from FAISS
    # This is tricky because FAISS uses internal IDs.
    # We need to find the internal IDs corresponding to this doc_id.
    try:
        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        
        # Find all keys in docstore where metadata['doc_id'] == doc_id
        ids_to_delete = []
        for internal_id, document in vectorstore.docstore._dict.items():
            if document.metadata.get("doc_id") == doc_id:
                ids_to_delete.append(internal_id)
        
        if ids_to_delete:
            vectorstore.delete(ids_to_delete)
            save_vectorstore(vectorstore)
    except Exception as e:
        # If vectorstore deletion fails, we might still want to delete from DB
        # or log it. The requirement says "note it" if not possible.
        print(f"Warning: Failed to delete from FAISS: {e}")

    # 3. Delete from DB
    db.delete(doc)
    db.commit()
    
    return {"status": "success", "message": f"Document {doc_id} deleted"}
