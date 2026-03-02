import os
import uuid
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import ChatRequest, FileMetadata
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.llm_manager import LLMManager
from app.services.session_manager import SessionManager

app = FastAPI(title="DocuChat AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
doc_processor = DocumentProcessor()
vector_store = VectorStore()
llm_manager = LLMManager()
session_manager = SessionManager()

# Ensure upload dir exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.post("/v1/upload")
async def upload_document(file: UploadFile = File(...), session_id: str = Form(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        chunks = doc_processor.process_pdf(file_path, file.filename)
        
        # Index in vector store
        vector_store.add_documents(chunks, session_id, file_id)
        
        # Update session
        file_meta = {
            "id": file_id,
            "filename": file.filename,
            "total_pages": len(set([c["metadata"]["page"] for c in chunks])),
            "status": "processed",
            "upload_time": datetime.now()
        }
        session_manager.add_file(session_id, file_meta)
        
        return file_meta
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/files")
async def list_files(session_id: str):
    return session_manager.get_files(session_id)

@app.delete("/v1/files/{file_id}")
async def delete_file(file_id: str, session_id: str):
    vector_store.delete_file_vectors(session_id, file_id)
    session_manager.remove_file(session_id, file_id)
    return {"status": "deleted"}

@app.post("/v1/chat")
async def chat(request: ChatRequest):
    # 1. Retrieve context
    context_chunks = vector_store.query(request.message, request.session_id)
    
    if not context_chunks:
        # Return a simple stream if no docs uploaded
        def empty_gen():
            yield "Please upload documents first to start chatting."
        return StreamingResponse(empty_gen(), media_type="text/event-stream")

    # 2. Generate streaming response
    return StreamingResponse(
        llm_manager.generate_response_stream(request.message, context_chunks),
        media_type="text/event-stream"
    )

@app.post("/v1/session/clear")
async def clear_session(session_id: str):
    vector_store.clear_session_vectors(session_id)
    session_manager.clear_session(session_id)
    return {"status": "session cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
