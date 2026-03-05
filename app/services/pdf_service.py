import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

def process_pdf(file_content: bytes, filename: str, session_id: str):
    doc = fitz.open(stream=file_content, filetype="pdf")
    chunks = []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        page_chunks = text_splitter.split_text(text)
        
        for chunk_text in page_chunks:
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk_text,
                "metadata": {
                    "session_id": session_id,
                    "filename": filename,
                    "page_number": page_num + 1
                }
            })
            
    return chunks, len(doc)
