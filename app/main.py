from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, UploadResponse
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreService
from app.services.chat_service import ChatService
import uuid

app = FastAPI(title="DocuChat AI API")

pdf_processor = PDFProcessor()
vector_store = VectorStoreService()
chat_service = ChatService()

@app.post("/api/v1/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        # Process PDF to chunks
        chunks = pdf_processor.process_pdf(content, file.filename)
        
        if not chunks:
            return UploadResponse(
                file_id="none",
                status="error",
                message="No text could be extracted from the PDF."
            )

        # Upsert to vector store in background to avoid blocking
        background_tasks.add_task(vector_store.upsert_documents, chunks, session_id)

        return UploadResponse(
            file_id=str(uuid.uuid4()),
            status="processing",
            message="Document is being processed and indexed."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_service.get_chat_response(
            query=request.query,
            session_id=request.session_id,
            history=request.history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/documents/{session_id}")
async def clear_session(session_id: str):
    try:
        await vector_store.delete_session_docs(session_id)
        return {"status": "success", "message": f"All documents for session {session_id} deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
