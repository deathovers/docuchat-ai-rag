import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Use a placeholder that we replace manually to avoid KeyError if context has braces
SYSTEM_PROMPT_TEMPLATE = """You are a document assistant. Answer the user's question using ONLY the provided context. 
If the answer is not in the context, say 'The answer was not found in the uploaded documents.' 

Always cite the document name and page number in your response text like [Source: filename, Page: #].
Additionally, you MUST return a JSON object with two keys:
1. "answer": Your detailed response string.
2. "used_source_indices": A list of integers representing the indices of the context chunks you actually used to form your answer.

Context:
[[CONTEXT_PLACEHOLDER]]
"""

async def generate_grounded_response(query: str, retrieved_chunks: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks):
        block = f"Index: {i}\nSource: {chunk['metadata']['filename']}, Page: {chunk['metadata']['page_number']}\nContent: {chunk['text']}"
        context_blocks.append(block)
    
    context_str = "\n\n".join(context_blocks)
    
    # Manual replacement to avoid KeyError from braces in context_str during .format()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("[[CONTEXT_PLACEHOLDER]]", context_str)
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    try:
        content = response.choices[0].message.content
        result = json.loads(content)
        answer = result.get("answer", "The answer was not found in the uploaded documents.")
        used_indices = result.get("used_source_indices", [])
    except (json.JSONDecodeError, KeyError):
        return {"answer": "Error parsing response from LLM.", "citations": []}

    citations = []
    seen_citations = set()
    for idx in used_indices:
        if 0 <= idx < len(retrieved_chunks):
            meta = retrieved_chunks[idx]['metadata']
            cite_key = (meta['filename'], meta['page_number'])
            if cite_key not in seen_citations:
                citations.append({
                    "document": meta['filename'],
                    "page": meta['page_number']
                })
                seen_citations.add(cite_key)

    return {
        "answer": answer,
        "citations": citations
    }
