import fitz  # PyMuPDF
import asyncio
import logging
import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
from pinecone import Pinecone
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Clients
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def process_pdf(file_path: str, session_id: str, file_name: str):
    \"\"\"
    Extracts text from PDF, chunks it, generates embeddings, and stores in Pinecone.
    \"\"\"
    try:
        # 1. Extract Text with Page Numbers
        doc = fitz.open(file_path)
        chunks_to_embed = []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            if not text.strip():
                continue
                
            page_chunks = text_splitter.split_text(text)
            for chunk in page_chunks:
                chunks_to_embed.append({
                    "text": chunk,
                    "page": page_num,
                    "file_name": file_name
                })
        
        doc.close()

        if not chunks_to_embed:
            logger.warning(f"No text extracted from {file_name}")
            return

        # 2. Generate Embeddings and Upsert in Batches
        batch_size = 100
        for i in range(0, len(chunks_to_embed), batch_size):
            batch = chunks_to_embed[i:i + batch_size]
            texts = [c["text"] for c in batch]
            
            # Async embedding generation
            embed_res = await aclient.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            
            vectors = []
            for j, emb_data in enumerate(embed_res.data):
                vectors.append({
                    "id": str(uuid.uuid4()),
                    "values": emb_data.embedding,
                    "metadata": {
                        "session_id": session_id,
                        "text": batch[j]["text"],
                        "page": batch[j]["page"],
                        "file_name": batch[j]["file_name"]
                    }
                })
            
            # Offload blocking upsert to thread
            await asyncio.to_thread(index.upsert, vectors=vectors)

        logger.info(f"Successfully ingested {file_name} for session {session_id}")

    except Exception as e:
        logger.error(f"Failed to process PDF {file_name}: {str(e)}", exc_info=True)
        raise e

async def delete_session_vectors(session_id: str):
    \"\"\"
    Deletes all vectors associated with a session.
    \"\"\"
    try:
        await asyncio.to_thread(
            index.delete,
            filter={"session_id": {"$eq": session_id}}
        )
    except Exception as e:
        logger.error(f"Error deleting vectors for session {session_id}: {str(e)}")
