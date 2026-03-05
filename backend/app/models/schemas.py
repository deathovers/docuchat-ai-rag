from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: str

class Citation(BaseModel):
    file_name: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]

class FileMetadata(BaseModel):
    file_id: str
    file_name: str
    total_pages: int
