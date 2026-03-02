from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import UploadResponse, ChatRequest, ChatResponse
from app.utils.pdf_processor import extract_text_from_pdf
from app.core.rag_engine import RAGEngine
from typing import List

router = APIRouter()
rag_engine = RAGEngine()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    pages_data = extract_text_from_pdf(content, file.filename)
    
    if not pages_data:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    
    doc_id = await rag_engine.process_and_store_document(session_id, pages_data, file.filename)
    
    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="ready",
        page_count=len(pages_data)
    )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer, citations = await rag_engine.get_answer(request.session_id, request.query)
    return ChatResponse(answer=answer, citations=citations)

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, session_id: str):
    await rag_engine.delete_document(session_id, doc_id)
    return {"status": "deleted"}
