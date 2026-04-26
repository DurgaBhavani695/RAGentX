from fastapi import FastAPI
from app.api.endpoints import ingest, chat
from app.database.session import engine
from app.database.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(ingest.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to RAGentX API"}
