from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
, Citation
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService

router = APIRouter()
vector_store = VectorStore()
llm_service = LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Retrieve relevant chunks
    chunks = await vector_store.query(request.session_id, request.query)
    
    # 2. Generate answer
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
    result = await llm_service.generate_answer(request.query, chunks, history_dicts)
    
    return ChatResponse(
        answer=result["answer"],
        citations=[Citation(document=c["document"], page=c["page"]) for c in result["citations"]]
    )
