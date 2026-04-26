import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, ChatHistory, DocMetadata
from app.database.session import get_db

# Use an in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_chat_history(db_session):
    chat = ChatHistory(
        session_id="test_session",
        role="user",
        content="Hello world"
    )
    db_session.add(chat)
    db_session.commit()
    db_session.refresh(chat)
    
    assert chat.id is not None
    assert chat.session_id == "test_session"
    assert chat.role == "user"
    assert chat.content == "Hello world"
    assert chat.timestamp is not None

def test_create_doc_metadata(db_session):
    doc = DocMetadata(
        doc_id="doc_1",
        filename="test.pdf",
        page_number=1,
        extra_info={"author": "test"}
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    
    assert doc.id is not None
    assert doc.doc_id == "doc_1"
    assert doc.filename == "test.pdf"
    assert doc.page_number == 1
    assert doc.extra_info == {"author": "test"}

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    try:
        assert db is not None
    finally:
        db.close()
