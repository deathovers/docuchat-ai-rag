from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.pdf_service import process_pdf
from app.services.vector_store import upsert_chunks
from app.models.document import DocumentInfo
import uuid

router = APIRouter()

@router.post("/upload", response_model=List[DocumentInfo])
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 files allowed per session.")
    
    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
            
        content = await file.read()
        chunks, page_count = process_pdf(content, file.filename, session_id)
        
        await upsert_chunks(chunks)
        
        results.append(DocumentInfo(
            id=str(uuid.uuid4()),
            name=file.filename,
            status="processed",
            page_count=page_count
        ))
        
    return results
