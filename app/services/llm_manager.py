from openai import OpenAI
from app.config import settings
from typing import List, Dict, Generator
import json

class LLMManager:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_response_stream(self, query: str, context_chunks: List[Dict]) -> Generator[str, None, None]:
        context_text = "\n\n".join([
            f"Source: {c['metadata']['source']}, Page: {c['metadata']['page']}\nContent: {c['text']}"
            for c in context_chunks
        ])

        system_prompt = (
            "You are a helpful assistant. Answer the question ONLY using the provided context. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Always cite the document name and page number for every claim in the format [Source: filename, Page: X].\n\n"
            f"Context:\n{context_text}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        stream = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        # After streaming the text, we could send citations as a final block
        # In SSE, we can use a specific event type or a marker
        citations = [c['metadata'] for c in context_chunks]
        yield f"\n\nCITATIONS_JSON:{json.dumps(citations)}"
