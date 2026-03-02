from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    page_count: int

class Citation(BaseModel):
    document_name: str
    page: int

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
