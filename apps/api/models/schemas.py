from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    id: str
    file_name: str
    file_size: int
    upload_timestamp: datetime
    page_count: int
    status: str

class SourceReference(BaseModel):
    document_name: str
    page_number: int

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[SourceReference]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    query: str
    session_id: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]

class UploadResponse(BaseModel):
    file_ids: List[str]
    status: str
