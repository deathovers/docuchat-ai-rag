from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.vector_store import search_vectors
from app.services.llm_service import get_chat_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Retrieve relevant chunks
    context_chunks = await search_vectors(request.query, request.session_id)
    
    # 2. Generate grounded response
    response_data = await get_chat_response(
        query=request.query,
        context_chunks=context_chunks,
        history=request.history
    )
    
    return ChatResponse(**response_data)
