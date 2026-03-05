from pydantic import BaseModel

class DocumentInfo(BaseModel):
    id: str
    name: str
    status: str
    page_count: int
