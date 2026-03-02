from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FileMetadata(BaseModel):
    id: str
    filename: str
    total_pages: int
    status: str
    upload_time: datetime

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[dict]
