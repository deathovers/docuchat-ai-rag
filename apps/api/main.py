import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid

from apps.api.models.schemas import ChatRequest, ChatResponse, UploadResponse, DocumentMetadata
from apps.api.services.pdf_processor import PDFProcessor
from apps.api.services.vector_store import VectorStore
from apps.api.services.llm_service import LLMService
from apps.api.config import settings

app = FastAPI(title="DocuChat AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
vector_store = VectorStore()
llm_service = LLMService(api_key=settings.OPENAI_API_KEY)

# Ensure upload dir exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/upload", response_model=UploadResponse)
async def upload_documents(session_id: str, files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents allowed per session.")
    
    file_ids = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
            
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process and index
        chunks = pdf_processor.process_pdf(file_path, file.filename, session_id)
        vector_store.upsert_chunks(chunks)
        
        file_ids.append(file_id)
        
    return UploadResponse(file_ids=file_ids, status="ready")

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Retrieve context
    context_chunks = vector_store.search(request.query, request.session_id, top_k=settings.TOP_K)
    
    # 2. Get LLM response
    result = await llm_service.get_chat_response(
        query=request.query,
        history=request.history,
        context_chunks=context_chunks
    )
    
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
