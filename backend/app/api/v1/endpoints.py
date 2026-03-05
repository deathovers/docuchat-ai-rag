from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, FileMetadata
from app.services.ingestion import process_pdf
from app.services.retrieval import get_chat_response

router = APIRouter(prefix="/v1")

@router.post("/upload", response_model=List[FileMetadata])
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: str = Header(..., alias="Session-ID")
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per session.")
    
    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        content = await file.read()
        res = await process_pdf(content, file.filename, session_id)
        results.append(res)
    
    return results

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await get_chat_response(request.query, request.session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
