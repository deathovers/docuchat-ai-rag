from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
from app.models.document import DocumentInfo
from app.services.pdf_service import PDFService
from app.services.vector_store import VectorStore

router = APIRouter()
pdf_service = PDFService()
vector_store = VectorStore()

@router.post("/upload", response_model=List[DocumentInfo])
async def upload_documents(session_id: str = Form(...), files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 files allowed per session.")
        
    results = []
    for file in files:
        content = await file.read()
        chunks, page_count = pdf_service.process_pdf(content, file.filename, session_id)
        
        await vector_store.upsert_chunks(chunks)
        
        results.append(DocumentInfo(
            id=str(uuid.uuid4()),
            name=file.filename,
            status="processed",
            page_count=page_count
        ))
        
    return results

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, session_id: str):
    # In a full implementation, we'd filter by doc_id too. 
    # For MVP, session cleanup is the priority.
    return {"status": "success"}
