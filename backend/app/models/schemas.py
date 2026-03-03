from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    file_name: str
    page: int

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class DocumentMetadata(BaseModel):
    file_id: str
    file_name: str
    status: str

class SessionDocumentsResponse(BaseModel):
    session_id: str
    documents: List[DocumentMetadata]
