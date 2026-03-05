from fastapi import APIRouter, Header, HTTPException, Body
from typing import List, Dict, Optional
from app.services.retrieval import get_chat_response
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = []

@router.post("/chat")
async def chat(
    request: ChatRequest,
    session_id: str = Header(..., alias="Session-ID")
):
    \"\"\"
    Endpoint to handle RAG-based chat queries.
    \"\"\"
    if not session_id:
        raise HTTPException(status_code=400, detail="Session-ID header is required")
    
    # Properly await the async service call
    response = await get_chat_response(
        session_id=session_id,
        query=request.query,
        history=request.history
    )
    
    return response
