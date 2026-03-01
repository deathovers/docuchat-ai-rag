import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.core.config import settings
import uuid

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def process_pdf(self, file_bytes: bytes, filename: str, session_id: str):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
            
            # Create chunks for this page
            chunks = self.text_splitter.split_text(text)
            
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "page": page_num + 1,
                        "session_id": session_id,
                        "document_id": str(uuid.uuid4())
                    }
                ))
        
        return documents
