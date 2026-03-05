from openai import OpenAI
from pinecone import Pinecone
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant. Answer questions ONLY based on the provided context. 
If the answer is not in the context, say 'The answer was not found in the uploaded documents.' 
Do not use outside knowledge.

Context:
{context}

Question: {query}
"""

async def get_chat_response(query: str, session_id: str):
    # 1. Embed query
    embedding_res = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_embedding = embedding_res.data[0].embedding

    # 2. Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=5,
        filter={"session_id": {"$eq": session_id}},
        include_metadata=True
    )

    # 3. Format context and citations
    context_parts = []
    citations = []
    seen_citations = set()

    for res in results["matches"]:
        meta = res["metadata"]
        context_parts.append(f"Source: {meta['file_name']} (Page {meta['page']})\nContent: {meta['text']}")
        
        cit_key = f"{meta['file_name']}_{meta['page']}"
        if cit_key not in seen_citations:
            citations.append({
                "file_name": meta["file_name"],
                "page": int(meta["page"])
            })
            seen_citations.add(cit_key)

    # 4. LLM Call
    context_str = "\n\n".join(context_parts)
    prompt = SYSTEM_PROMPT.format(context=context_str, query=query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    return {
        "answer": response.choices[0].message.content,
        "citations": citations
    }
