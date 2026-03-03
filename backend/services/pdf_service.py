import fitz  # PyMuPDF

def extract_text_with_pages(file_content: bytes):
    doc = fitz.open(stream=file_content, filetype="pdf")
    pages_data = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages_data.append({
                "text": text,
                "page": page_num + 1
            })
    return pages_data
