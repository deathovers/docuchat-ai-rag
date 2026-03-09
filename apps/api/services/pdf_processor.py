import fitz  # PyMuPDF
from typing import List, Dict, Any
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from apps.api.config import settings

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )

    def process_pdf(self, file_path: str, file_name: str, session_id: str) -> List[Dict[str, Any]]:
        doc = fitz.open(file_path)
        chunks = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            page_chunks = self.text_splitter.split_text(text)
            
            for chunk_text in page_chunks:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "metadata": {
                        "session_id": session_id,
                        "document_name": file_name,
                        "page_number": page_num + 1,
                        "file_name": file_name
                    }
                })
        
        doc.close()
        return chunks
