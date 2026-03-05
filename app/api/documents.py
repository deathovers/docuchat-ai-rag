import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.document import DocumentInfo
from app.services.pdf_service import extract_text_from_pdf, chunk_documents
from app.services.vector_store import upsert_chunks, delete_session_vectors

router = APIRouter()

@router.post("/upload", response_model=List[DocumentInfo])
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed.")

    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
            
        content = await file.read()
        pages_data = extract_text_from_pdf(content, file.filename)
        chunks = chunk_documents(pages_data)
        
        await upsert_chunks(session_id, chunks)
        
        results.append(DocumentInfo(
            id=str(uuid.uuid4()),
            name=file.filename,
            status="processed",
            page_count=len(pages_data)
        ))
        
    return results

@router.delete("/documents/{session_id}")
async def clear_session(session_id: str):
    try:
        await delete_session_vectors(session_id)
        return {"message": "Session data cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
