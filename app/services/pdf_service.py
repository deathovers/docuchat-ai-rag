import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

class PDFService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def process_pdf(self, file_bytes: bytes, filename: str, session_id: str) -> List[Dict[str, Any]]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        chunks = []
        
        page_count = len(doc)
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            page_chunks = self.splitter.split_text(text)
            for chunk in page_chunks:
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "session_id": session_id,
                        "filename": filename,
                        "page_number": page_num + 1
                    }
                })
        return chunks, page_count
