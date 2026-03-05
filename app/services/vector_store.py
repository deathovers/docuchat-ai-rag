import uuid
from typing import List, Dict, Any
from pinecone import Pinecone
from openai import AsyncOpenAI
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    response = await openai_client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [e.embedding for e in response.data]

async def upsert_chunks(session_id: str, chunks: List[Dict[str, Any]]):
    texts = [c["text"] for c in chunks]
    embeddings = await get_embeddings(texts)
    
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "text": chunk["text"],
                "session_id": session_id,
                "filename": chunk["metadata"]["filename"],
                "page_number": chunk["metadata"]["page_number"]
            }
        })
    
    # Pinecone upsert in batches of 100
    for i in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[i:i+100])

async def query_vector_store(session_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    query_embedding_res = await openai_client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_embedding = query_embedding_res.data[0].embedding
    
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"session_id": {"$eq": session_id}},
        include_metadata=True
    )
    
    retrieved = []
    for match in results["matches"]:
        retrieved.append({
            "text": match["metadata"]["text"],
            "metadata": {
                "filename": match["metadata"]["filename"],
                "page_number": int(match["metadata"]["page_number"])
            }
        })
    return retrieved

async def delete_session_vectors(session_id: str):
    index.delete(filter={"session_id": {"$eq": session_id}})
