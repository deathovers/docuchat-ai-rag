from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.config import settings
from app.services.vector_store import VectorStoreService
from app.models.schemas import ChatResponse, Source
import re

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0
        )
        self.vector_store = VectorStoreService()

    async def get_chat_response(self, query: str, session_id: str, history: list) -> ChatResponse:
        # 1. Retrieve relevant context
        matches = await self.vector_store.query_similar(query, session_id)
        
        context_text = ""
        sources = []
        seen_sources = set()

        for match in matches:
            meta = match.metadata
            context_text += f"\n---\nSource: {meta['file_name']}, Page: {int(meta['page_number'])}\nContent: {meta['text_content']}\n"
            
            source_key = f"{meta['file_name']}-{int(meta['page_number'])}"
            if source_key not in seen_sources:
                sources.append(Source(file_name=meta['file_name'], page=int(meta['page_number'])))
                seen_sources.add(source_key)

        # 2. Construct Prompt
        system_prompt = (
            "You are a helpful AI assistant. Answer only based on the provided context. "
            "If the answer is not present, state: 'The answer was not found in the uploaded documents.' "
            "Every factual statement must be followed by a citation in the format [Source Name, Page X]. "
            "Context:\n" + context_text
        )

        messages = [SystemMessage(content=system_prompt)]
        
        # Add history (last 5 messages)
        for msg in history[-5:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(SystemMessage(content=msg.content))
        
        messages.append(HumanMessage(content=query))

        # 3. Call LLM
        response = await self.llm.ainvoke(messages)
        answer = response.content

        return ChatResponse(answer=answer, sources=sources)
