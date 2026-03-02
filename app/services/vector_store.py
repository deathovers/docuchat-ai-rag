from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from app.config import settings
from typing import List, Dict
import uuid

class VectorStoreService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )

    async def upsert_documents(self, chunks: List[Dict], session_id: str):
        vectors = []
        for chunk in chunks:
            # Generate embedding for the chunk text
            embedding = self.embeddings.embed_query(chunk["text"])
            
            # Create a unique ID for the vector
            vector_id = str(uuid.uuid4())
            
            # Prepare metadata including session_id for isolation
            metadata = chunk["metadata"]
            metadata["session_id"] = session_id
            metadata["text_content"] = chunk["text"]
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
            
            # Batch upsert to Pinecone (limit 100 per call for stability)
            if len(vectors) >= 100:
                self.index.upsert(vectors=vectors)
                vectors = []
        
        if vectors:
            self.index.upsert(vectors=vectors)

    async def query_similar(self, query: str, session_id: str, top_k: int = 5):
        query_embedding = self.embeddings.embed_query(query)
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter={"session_id": {"$eq": session_id}},
            include_metadata=True
        )
        
        return results.matches

    async def delete_session_docs(self, session_id: str):
        self.index.delete(filter={"session_id": {"$eq": session_id}})
