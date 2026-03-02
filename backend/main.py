from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.pdf_processor import extract_text_from_pdf
from .core.vector_store import VectorStoreManager
from .core.rag import get_chat_response
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uvicorn

app = FastAPI(title="DocuChat AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_manager = VectorStoreManager()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

@app.post("/api/v1/upload")
async def upload_document(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    documents = extract_text_from_pdf(content, file.filename, session_id)
    
    if not documents:
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")
    
    chunks = text_splitter.split_documents(documents)
    vector_manager.add_documents(chunks)
    
    return {"file_id": documents[0].metadata["file_id"], "status": "success"}

@app.post("/api/v1/chat")
async def chat(session_id: str, message: str):
    try:
        response = get_chat_response(session_id, message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/document/{file_id}")
async def delete_document(file_id: str, session_id: str):
    vector_manager.delete_by_file_id(session_id, file_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
