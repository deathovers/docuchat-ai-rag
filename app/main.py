from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="DocuChat AI API")

app.include_router(api_router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "DocuChat AI API is running"}
