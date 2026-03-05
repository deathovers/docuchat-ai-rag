from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.vector_store import query_vector_store
from app.services.llm_service import generate_grounded_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Retrieve relevant chunks
        chunks = await query_vector_store(request.session_id, request.query)
        
        if not chunks:
            return ChatResponse(
                answer="No documents found for this session. Please upload PDFs first.",
                citations=[]
            )
        
        # 2. Generate response with history
        history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
        result = await generate_grounded_response(request.query, chunks, history_dicts)
        
        return ChatResponse(
            answer=result["answer"],
            citations=result["citations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
