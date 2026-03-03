from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Source(BaseModel):
    file_name: str
    page_number: int

class ChatRequest(BaseModel):
    session_id: str
    message: str
    stream: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class FileMetadata(BaseModel):
    document_id: str
    filename: str
    page_count: int
    upload_timestamp: datetime
    session_id: str

class SessionClearRequest(BaseModel):
    session_id: str
