import pytest
import os
import shutil
import tempfile
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.models import Base, DocMetadata, AppConfig
from app.retrieval.document_loaders import load_file_to_documents

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Setup fresh DB for each test
    from app.database.session import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    # Seed default configs
    defaults = [
        {"key": "max_file_size_mb", "value": 5},
        {"key": "max_files_per_upload", "value": 5},
        {"key": "max_total_files", "value": 10}
    ]
    for d in defaults:
        db.add(AppConfig(**d))
    
    db.commit()
    db.close()
    
    if os.path.exists("data/uploads"):
        shutil.rmtree("data/uploads")
    os.makedirs("data/uploads", exist_ok=True)
    
    if os.path.exists("vectorstore"):
        shutil.rmtree("vectorstore")
        
    yield

def test_load_file_to_documents_txt():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as tmp:
        tmp.write("Hello World from text file")
        tmp_path = tmp.name
    
    try:
        docs = load_file_to_documents(tmp_path, metadata={"source": "test_txt"})
        assert len(docs) >= 1
        assert "Hello World" in docs[0].page_content
        assert docs[0].metadata["source"] == "test_txt"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_upload_file_success():
    file_content = b"This is a test file content for ingestion."
    response = client.post(
        "/ingest/file",
        files={"files": ("test_upload.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify DB entry
    db = SessionLocal()
    doc = db.query(DocMetadata).filter(DocMetadata.filename == "test_upload.txt").first()
    assert doc is not None
    assert doc.file_size == len(file_content)
    assert os.path.exists(doc.file_path)
    db.close()

def test_upload_multiple_files_success():
    files = [
        ("files", ("file1.txt", b"content1", "text/plain")),
        ("files", ("file2.txt", b"content2", "text/plain"))
    ]
    response = client.post("/ingest/file", files=files)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

def test_upload_file_exceeds_max_size():
    # Set limit to 0.000001 MB (approx 1 byte)
    db = SessionLocal()
    config = db.query(AppConfig).filter(AppConfig.key == "max_file_size_mb").first()
    config.value = 0.000001 
    db.commit()
    db.close()
    
    file_content = b"This content is definitely more than 1 byte."
    response = client.post(
        "/ingest/file",
        files={"files": ("large_file.txt", file_content, "text/plain")}
    )
    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()

def test_upload_exceeds_max_files_per_upload():
    # Limit is 5 by default. Try 6.
    files = [("files", (f"file{i}.txt", b"content", "text/plain")) for i in range(6)]
    response = client.post("/ingest/file", files=files)
    assert response.status_code == 400
    assert "too many files" in response.json()["detail"].lower()

def test_upload_exceeds_max_total_files():
    # Limit is 10. Pre-fill 9. Try uploading 2.
    db = SessionLocal()
    for i in range(9):
        db.add(DocMetadata(doc_id=str(uuid.uuid4()), filename=f"old{i}.txt"))
    db.commit()
    db.close()
    
    files = [
        ("files", ("new1.txt", b"content", "text/plain")),
        ("files", ("new2.txt", b"content", "text/plain"))
    ]
    response = client.post("/ingest/file", files=files)
    assert response.status_code == 400
    assert "total limit" in response.json()["detail"].lower()

def test_list_documents():
    db = SessionLocal()
    doc_id = str(uuid.uuid4())
    db.add(DocMetadata(doc_id=doc_id, filename="test_list.txt"))
    db.commit()
    db.close()
    
    response = client.get("/ingest/documents")
    assert response.status_code == 200
    docs = response.json()
    assert any(d["doc_id"] == doc_id for d in docs)

def test_download_document():
    # Create a dummy file
    filename = "test_download.txt"
    file_path = os.path.join("data/uploads", filename)
    os.makedirs("data/uploads", exist_ok=True)
    with open(file_path, "w") as f:
        f.write("download content")
    
    db = SessionLocal()
    doc_id = str(uuid.uuid4())
    db.add(DocMetadata(doc_id=doc_id, filename=filename, file_path=file_path))
    db.commit()
    db.close()
    
    response = client.get(f"/ingest/documents/{doc_id}/download")
    assert response.status_code == 200
    assert response.content == b"download content"

def test_delete_document():
    filename = "test_delete.txt"
    file_path = os.path.join("data/uploads", filename)
    os.makedirs("data/uploads", exist_ok=True)
    with open(file_path, "w") as f:
        f.write("delete content")
    
    db = SessionLocal()
    doc_id = str(uuid.uuid4())
    db.add(DocMetadata(doc_id=doc_id, filename=filename, file_path=file_path))
    db.commit()
    db.close()
    
    # Verify file exists
    assert os.path.exists(file_path)
    
    response = client.delete(f"/ingest/documents/{doc_id}")
    assert response.status_code == 200
    
    # Verify file deleted
    assert not os.path.exists(file_path)
    
    # Verify DB entry deleted
    db = SessionLocal()
    doc = db.query(DocMetadata).filter(DocMetadata.doc_id == doc_id).first()
    assert doc is None
    db.close()
