from pinecone import Pinecone
from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, Any
import uuid

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = await self.openai_client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [data.embedding for data in response.data]

    async def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        embeddings = await self.get_embeddings(texts)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embeddings[i],
                "metadata": {
                    **chunk["metadata"],
                    "text": chunk["text"]
                }
            })
        
        # Batch upsert
        self.index.upsert(vectors=vectors)

    async def query(self, session_id: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = await self.get_embeddings([query_text])
        
        results = self.index.query(
            vector=query_embedding[0],
            top_k=top_k,
            filter={"session_id": {"$eq": session_id}},
            include_metadata=True
        )
        
        return [
            {
                "text": match.metadata["text"],
                "filename": match.metadata["filename"],
                "page_number": int(match.metadata["page_number"])
            }
            for match in results.matches
        ]

    async def delete_session_data(self, session_id: str):
        self.index.delete(filter={"session_id": {"$eq": session_id}})
