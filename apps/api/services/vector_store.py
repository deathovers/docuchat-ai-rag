from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from apps.api.config import settings
from typing import List, Dict, Any

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        vectors = []
        texts = [c["text"] for c in chunks]
        embeds = self.embeddings.embed_documents(texts)
        
        for i, chunk in enumerate(chunks):
            vectors.append({
                "id": chunk["id"],
                "values": embeds[i],
                "metadata": {
                    **chunk["metadata"],
                    "text": chunk["text"]
                }
            })
        
        # Batch upsert
        self.index.upsert(vectors=vectors)

    def search(self, query: str, session_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.embeddings.embed_query(query)
        
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            filter={"session_id": {"$eq": session_id}},
            include_metadata=True
        )
        
        return [
            {
                "id": match["id"],
                "score": match["score"],
                "text": match["metadata"]["text"],
                "metadata": match["metadata"]
            }
            for match in results["matches"]
        ]

    def delete_by_session(self, session_id: str):
        # Note: Pinecone delete by filter might require a specific setup or index type
        # For simplicity, we assume the index supports it or we use namespaces
        self.index.delete(filter={"session_id": {"$eq": session_id}})
