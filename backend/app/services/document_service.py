import fitz  # PyMuPDF
import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.services.vector_store import VectorStoreService

class DocumentService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def process_pdf(self, file_bytes: bytes, filename: str, session_id: str):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        file_id = str(uuid.uuid4())
        chunks = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
            
            page_chunks = self.text_splitter.split_text(text)
            for chunk in page_chunks:
                chunks.append(Document(
                    page_content=chunk,
                    metadata={
                        "session_id": session_id,
                        "file_id": file_id,
                        "file_name": filename,
                        "page_number": page_num + 1
                    }
                ))
        
        if chunks:
            self.vector_store.add_documents(chunks)
        
        return {"file_id": file_id, "file_name": filename}
