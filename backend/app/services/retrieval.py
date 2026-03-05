import asyncio
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI, RateLimitError, APITimeoutError
from pinecone import Pinecone
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Clients
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_chat_response(session_id: str, query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    \"\"\"
    Retrieves relevant document chunks and generates a cited response using RAG.
    \"\"\"
    try:
        # 1. Generate Query Embedding (Async)
        embed_res = await aclient.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_vector = embed_res.data[0].embedding

        # 2. Search Pinecone (Offload blocking call to thread)
        # Pinecone's standard SDK is synchronous; we use asyncio.to_thread to keep the loop free.
        search_res = await asyncio.to_thread(
            index.query,
            vector=query_vector,
            top_k=5,
            filter={"session_id": {"$eq": session_id}},
            include_metadata=True
        )

        # 3. Process Context and Citations
        context_parts = []
        citations = []
        seen_citations = set()

        for match in search_res.get("matches", []):
            meta = match.get("metadata", {})
            text = meta.get("text", "")
            file_name = meta.get("file_name", "Unknown")
            
            # Safe page conversion to handle non-numeric or missing data
            try:
                page_raw = meta.get("page", 0)
                page = int(float(page_raw))
            except (ValueError, TypeError):
                page = 0

            context_parts.append(f"Source: {file_name}, Page: {page}\nContent: {text}")
            
            cite_key = f"{file_name}-{page}"
            if cite_key not in seen_citations:
                citations.append({"file_name": file_name, "page": page})
                seen_citations.add(cite_key)

        if not context_parts:
            return {
                "answer": "The answer was not found in the uploaded documents.",
                "citations": []
            }

        context_str = "\n\n---\n\n".join(context_parts)

        # 4. Construct Prompt
        system_prompt = (
            "You are a helpful assistant. Answer questions ONLY based on the provided context. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Do not use outside knowledge."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        # Include a window of history for conversational context
        messages.extend(history[-5:]) 
        messages.append({"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"})

        # 5. LLM Inference (Async)
        response = await aclient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0
        )

        answer = response.choices[0].message.content

        # Only return citations if the model found an answer
        final_citations = citations if "The answer was not found" not in answer else []

        return {
            "answer": answer,
            "citations": final_citations
        }

    except RateLimitError:
        logger.error("OpenAI Rate Limit Exceeded")
        return {"answer": "I'm receiving too many requests right now. Please try again in a moment.", "citations": []}
    except APITimeoutError:
        logger.error("OpenAI API Timeout")
        return {"answer": "The request timed out. Please try again.", "citations": []}
    except Exception as e:
        logger.error(f"Error in retrieval service: {str(e)}", exc_info=True)
        return {"answer": "An internal error occurred while processing your request.", "citations": []}
