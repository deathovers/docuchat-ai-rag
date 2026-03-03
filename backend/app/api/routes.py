from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, SessionDocumentsResponse, DocumentMetadata
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/v1")
doc_service = DocumentService()
chat_service = ChatService()
vector_store = VectorStoreService()

@router.post("/upload", status_code=201)
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per session.")
    
    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        
        content = await file.read()
        if len(content) > 10 * 1024 * 1024: # 10MB
            continue
            
        res = await doc_service.process_pdf(content, file.filename, session_id)
        results.append(res)
        
    return {"message": f"Successfully processed {len(results)} files", "files": results}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await chat_service.get_chat_response(request.session_id, request.query)

@router.get("/documents/{session_id}", response_model=SessionDocumentsResponse)
async def get_documents(session_id: str):
    files_dict = vector_store.list_session_files(session_id)
    docs = [
        DocumentMetadata(file_id=fid, file_name=fname, status="indexed")
        for fid, fname in files_dict.items()
    ]
    return SessionDocumentsResponse(session_id=session_id, documents=docs)

@router.delete("/documents/{session_id}/{file_id}")
async def delete_document(session_id: str, file_id: str):
    vector_store.delete_session_docs(session_id, file_id)
    return {"message": "Document deleted successfully"}
