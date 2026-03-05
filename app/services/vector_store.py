from pinecone import Pinecone
from app.core.config import settings
import openai

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def upsert_chunks(chunks: list):
    vectors = []
    for chunk in chunks:
        embedding = get_embedding(chunk['text'])
        vectors.append({
            "id": chunk['id'],
            "values": embedding,
            "metadata": {
                **chunk['metadata'],
                "text": chunk['text']
            }
        })
    
    # Batch upsert
    index.upsert(vectors=vectors)

async def search_vectors(query: str, session_id: str, top_k: int = 5):
    query_vector = get_embedding(query)
    
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        filter={"session_id": {"$eq": session_id}},
        include_metadata=True
    )
    
    formatted_results = []
    for match in results['matches']:
        formatted_results.append({
            "text": match['metadata']['text'],
            "metadata": match['metadata']
        })
        
    return formatted_results

async def delete_session_vectors(session_id: str):
    index.delete(filter={"session_id": {"$eq": session_id}})
