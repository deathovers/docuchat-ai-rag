from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, DocumentMetadata
from app.core.document_processor import DocumentProcessor
from app.core.rag_engine import RAGEngine
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1")
doc_processor = DocumentProcessor()
rag_engine = RAGEngine()

# In-memory store for document tracking
active_documents = {}

@router.post("/upload")
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 25MB limit.")
            
        documents = doc_processor.process_pdf(content, file.filename, session_id)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No text layer found in PDF.")
            
        rag_engine.add_documents(documents)
        
        doc_id = str(uuid.uuid4())
        doc_meta = DocumentMetadata(
            document_id=doc_id,
            filename=file.filename,
            upload_timestamp=datetime.now().isoformat(),
            total_pages=len(set(d.metadata["page"] for d in documents)),
            status="indexed"
        )
        
        if session_id not in active_documents:
            active_documents[session_id] = []
        active_documents[session_id].append(doc_meta)
        
        return doc_meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def get_documents(session_id: str):
    return active_documents.get(session_id, [])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer, sources = await rag_engine.chat(request.session_id, request.message)
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
