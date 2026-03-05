import openai
from app.core.config import settings
from app.models.chat import Message

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a document assistant. Answer the user's question using ONLY the provided context. 
If the answer is not in the context, say 'The answer was not found in the uploaded documents.' 
Always cite the document name and page number for every piece of information you provide.

Context:
{context}
"""

def format_context(chunks):
    context_parts = []
    citations = []
    for chunk in chunks:
        metadata = chunk.get('metadata', {})
        filename = metadata.get('filename', 'Unknown')
        page = metadata.get('page_number', 'Unknown')
        text = chunk.get('text', '')
        
        context_parts.append(f"--- Source: {filename}, Page: {page} ---\n{text}")
        citations.append({"document": filename, "page": page})
    
    return "\n\n".join(context_parts), citations

async def get_chat_response(query: str, context_chunks: list, history: list[Message]):
    context_text, citations = format_context(context_chunks)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)}]
    
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    
    messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0
    )
    
    answer = response.choices[0].message.content
    
    # Deduplicate citations
    unique_citations = []
    seen = set()
    for c in citations:
        key = f"{c['document']}_{c['page']}"
        if key not in seen:
            unique_citations.append(c)
            seen.add(key)

    return {
        "answer": answer,
        "citations": unique_citations
    }
