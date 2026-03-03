from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.models.schemas import ChatRequest, ChatResponse, FileMetadata, SessionClearRequest
from app.services import pdf_service, vector_service, llm_service

router = APIRouter()

# In-memory store for file metadata (MVP only)
# In production, this would be a database
file_registry = {}

@router.post("/upload", response_model=FileMetadata)
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    
    # 1. Extract text and pages
    pages_content = pdf_service.extract_text_from_pdf(content, file.filename)
    
    # 2. Chunk documents
    chunks = pdf_service.chunk_docs(pages_content, session_id)
    
    # 3. Upsert to Vector DB
    vector_service.upsert_documents(chunks)
    
    # 4. Register metadata
    doc_id = str(uuid.uuid4())
    metadata = FileMetadata(
        document_id=doc_id,
        filename=file.filename,
        page_count=len(pages_content),
        upload_timestamp=datetime.now(),
        session_id=session_id
    )
    
    if session_id not in file_registry:
        file_registry[session_id] = []
    file_registry[session_id].append(metadata)
    
    return metadata

@router.get("/files", response_model=List[FileMetadata])
async def list_files(session_id: str):
    return file_registry.get(session_id, [])

@router.delete("/files/{filename}")
async def delete_file(session_id: str, filename: str):
    vector_service.delete_file_vectors(session_id, filename)
    if session_id in file_registry:
        file_registry[session_id] = [f for f in file_registry[session_id] if f.filename != filename]
    return {"status": "deleted"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Retrieve context
    contexts = vector_service.query_documents(request.message, request.session_id)
    
    # 2. Generate answer
    response = llm_service.generate_answer(request.message, contexts)
    
    return response

@router.post("/session/clear")
async def clear_session(request: SessionClearRequest):
    vector_service.delete_session_vectors(request.session_id)
    if request.session_id in file_registry:
        del file_registry[request.session_id]
    return {"status": "session cleared"}
