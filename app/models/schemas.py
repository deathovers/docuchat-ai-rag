from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    query: str
    history: Optional[List[ChatMessage]] = []

class Source(BaseModel):
    file_name: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class UploadResponse(BaseModel):
    file_id: str
    status: str
    message: str

class DocumentInfo(BaseModel):
    file_name: str
    file_id: str
