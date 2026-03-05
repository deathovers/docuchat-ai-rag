from fastapi import FastAPI
from app.api import chat, documents

app = FastAPI(title="DocuChat AI API")

app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(documents.router, prefix="/v1", tags=["documents"])

@app.get("/")
async def root():
    return {"message": "DocuChat AI API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
