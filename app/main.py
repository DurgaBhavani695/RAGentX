from fastapi import FastAPI
from app.api.endpoints import ingest, chat

app = FastAPI()

app.include_router(ingest.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to RAGentX API"}
