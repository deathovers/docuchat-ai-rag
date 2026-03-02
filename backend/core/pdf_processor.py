import fitz  # PyMuPDF
from langchain.schema import Document
import uuid

def extract_text_from_pdf(file_bytes: bytes, file_name: str, session_id: str) -> list[Document]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    documents = []
    file_id = str(uuid.uuid4())
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            metadata = {
                "file_name": file_name,
                "page_number": page_num + 1,
                "session_id": session_id,
                "file_id": file_id
            }
            documents.append(Document(page_content=text, metadata=metadata))
    
    return documents
