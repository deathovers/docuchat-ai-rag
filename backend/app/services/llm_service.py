import json
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.models.schemas import ChatResponse, Source

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a helpful assistant that answers questions based ONLY on the provided context.
Strictly follow these rules:
1. Answer the question using only the provided context.
2. If the answer is not contained within the context, state: "I'm sorry, but I couldn't find information about that in the uploaded documents."
3. Do not use any outside knowledge.
4. Provide your response in a clear, concise manner.
5. You must identify which parts of the context you used to answer the question.
"""

def generate_answer(query: str, contexts: List[Dict[str, Any]]) -> ChatResponse:
    if not contexts:
        return ChatResponse(
            answer="I'm sorry, but I couldn't find information about that in the uploaded documents.",
            sources=[]
        )

    context_text = ""
    for i, ctx in enumerate(contexts):
        context_text += f"[Source {i}]: {ctx['text']}\n\n"

    user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content
    
    sources = []
    seen_sources = set()
    for ctx in contexts:
        source_key = f"{ctx['file_name']}-{ctx['page_number']}"
        if source_key not in seen_sources:
            sources.append(Source(
                file_name=ctx['file_name'],
                page_number=ctx['page_number']
            ))
            seen_sources.add(source_key)

    return ChatResponse(answer=answer, sources=sources)
