from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    query: str
    history: List[Message] = []

class Citation(BaseModel):
    document: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
