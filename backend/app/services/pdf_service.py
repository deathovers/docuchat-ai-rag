import pdfplumber
from io import BytesIO
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def extract_text_from_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    pages_content = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_content.append({
                    "text": text,
                    "page_number": i + 1,
                    "file_name": filename
                })
    return pages_content

def chunk_docs(pages_content: List[Dict[str, Any]], session_id: str) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    documents = []
    for page in pages_content:
        chunks = text_splitter.split_text(page["text"])
        for chunk in chunks:
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "file_name": page["file_name"],
                    "page_number": page["page_number"],
                    "session_id": session_id
                }
            ))
    return documents
