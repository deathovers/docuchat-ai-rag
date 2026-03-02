import fitz  # PyMuPDF
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def process_pdf(self, file_bytes: bytes, file_name: str) -> List[Dict]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        chunks_with_metadata = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
            
            # Split text into chunks while preserving page metadata
            page_chunks = self.text_splitter.split_text(text)
            
            for chunk in page_chunks:
                chunks_with_metadata.append({
                    "text": chunk,
                    "metadata": {
                        "file_name": file_name,
                        "page_number": page_num + 1,
                    }
                })
        
        doc.close()
        return chunks_with_metadata
