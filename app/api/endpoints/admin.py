from fastapi import APIRouter, HTTPException, Body
from app.core.config import settings

router = APIRouter()

@router.get("/config")
async def get_config():
    return settings.model_dump()

@router.put("/config/{key}")
async def update_config(key: str, value: str = Body(...)):
    if not hasattr(settings, key):
        raise HTTPException(status_code=404, detail=f"Configuration key '{key}' not found")
    
    setattr(settings, key, value)
    return {key: getattr(settings, key)}
