import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pinecone import Pinecone
from app.core.config import settings
import uuid

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

async def process_pdf(file_content: bytes, file_name: str, session_id: str):
    doc = fitz.open(stream=file_content, filetype="pdf")
    file_id = str(uuid.uuid4())
    
    vectors = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        chunks = text_splitter.split_text(text)
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding_res = client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
            embedding = embedding_res.data[0].embedding
            
            vector_id = f"{file_id}_{page_num}_{i}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "session_id": session_id,
                    "file_name": file_name,
                    "page": page_num + 1,
                    "text": chunk,
                    "file_id": file_id
                }
            })
            
            # Batch upsert every 50 vectors
            if len(vectors) >= 50:
                index.upsert(vectors=vectors)
                vectors = []

    if vectors:
        index.upsert(vectors=vectors)
        
    return {"file_id": file_id, "file_name": file_name, "total_pages": len(doc)}
