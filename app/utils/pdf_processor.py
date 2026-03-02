import fitz  # PyMuPDF
from typing import List, Dict

def extract_text_from_pdf(file_content: bytes, filename: str) -> List[Dict]:
    doc = fitz.open(stream=file_content, filetype="pdf")
    pages_data = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():
            pages_data.append({
                "text": text,
                "page_number": page_num + 1,
                "filename": filename
            })
    return pages_data
