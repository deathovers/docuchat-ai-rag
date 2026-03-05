import json
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        context_text = ""
        for chunk in context_chunks:
            context_text += f"[Source: {chunk['filename']}, Page: {chunk['page_number']}] {chunk['text']}\n\n"

        system_prompt = (
            "You are a document assistant. Answer the user's question using ONLY the provided context. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Always cite the document name and page number in your response. "
            "Your response must be a JSON object with two keys: 'answer' (string) and 'citations' (list of objects with 'document' and 'page')."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"})

        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM returned empty content")

            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {content}")
                return {
                    "answer": "Error: The assistant returned an invalid response format.",
                    "citations": []
                }

            if not isinstance(data, dict):
                logger.error(f"LLM returned non-object JSON: {data}")
                return {
                    "answer": "Error: The assistant returned an unexpected data structure.",
                    "citations": []
                }

            return {
                "answer": data.get("answer", "No answer provided."),
                "citations": data.get("citations", [])
            }

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {"answer": "Error: AI service communication failure.", "citations": []}
        except Exception as e:
            logger.exception(f"Unexpected error in LLM service: {str(e)}")
            return {"answer": "An unexpected error occurred.", "citations": []}
