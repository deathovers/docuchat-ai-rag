from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.services.pdf_service import extract_text_with_pages
from backend.services.rag_service import RAGService
import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()

# In-memory store for file metadata (MVP)
session_files = {}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    pages_data = extract_text_with_pages(content)
    
    await rag_service.ingest_pdf(pages_data, file.filename, session_id)
    
    if session_id not in session_files:
        session_files[session_id] = []
    session_files[session_id].append(file.filename)
    
    return {"filename": file.filename, "status": "processed"}

@app.get("/files/{session_id}")
async def list_files(session_id: str):
    return {"files": session_files.get(session_id, [])}

@app.post("/query")
async def query_documents(data: dict):
    session_id = data.get("session_id")
    question = data.get("question")
    
    if not session_id or not question:
        raise HTTPException(status_code=400, detail="Missing session_id or question")

    chain = rag_service.get_chat_chain(session_id)
    
    async def event_generator():
        # Note: LangChain ConversationalRetrievalChain streaming is complex with source docs.
        # For MVP, we'll simulate streaming or use a simpler chain if needed.
        # Here we use the standard call and stream the result.
        response = await chain.ainvoke({"question": question, "chat_history": []})
        
        answer = response["answer"]
        sources = []
        for doc in response["source_documents"]:
            sources.append({
                "file_name": doc.metadata.get("source"),
                "page": doc.metadata.get("page")
            })
        
        # Stream the answer in chunks
        for i in range(0, len(answer), 20):
            yield f"data: {json.dumps({'content': answer[i:i+20], 'done': False})}\n\n"
            await asyncio.sleep(0.05)
            
        yield f"data: {json.dumps({'content': '', 'sources': sources, 'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    # In a real app, we'd delete from Pinecone here
    # rag_service.pc.Index(settings.PINECONE_INDEX_NAME).delete(delete_all=True, namespace=session_id)
    if session_id in session_files:
        del session_files[session_id]
    return {"status": "session cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
