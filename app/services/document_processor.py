import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import os
from app.config import settings

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def process_pdf(self, file_path: str, filename: str) -> List[Dict]:
        doc = fitz.open(file_path)
        chunks = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            page_chunks = self.text_splitter.split_text(text)
            for chunk in page_chunks:
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "source": filename,
                        "page": page_num + 1
                    }
                })
        
        doc.close()
        return chunks
