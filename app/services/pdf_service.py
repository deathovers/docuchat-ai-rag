import fitz  # PyMuPDF
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_data = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages_data.append({
            "text": text,
            "page_number": page_num + 1,
            "filename": filename
        })
    return pages_data

def chunk_documents(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    chunks = []
    for page in pages_data:
        texts = splitter.split_text(page["text"])
        for text in texts:
            chunks.append({
                "text": text,
                "metadata": {
                    "filename": page["filename"],
                    "page_number": page["page_number"]
                }
            })
    return chunks
