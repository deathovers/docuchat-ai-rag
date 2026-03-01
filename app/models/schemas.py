from pydantic import BaseModel
from typing import List, Optional

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    upload_timestamp: str
    total_pages: int
    status: str

class Citation(BaseModel):
    file: str
    page: int

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Citation]
