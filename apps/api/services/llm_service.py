import logging
import json
import tiktoken
from typing import List, Dict, Any, Tuple, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("OpenAI API Key is required.")
        
        self.model_name = model_name
        self.llm = ChatOpenAI(
            api_key=api_key, 
            model=model_name, 
            streaming=False, # Set to False for simpler implementation in this step
            temperature=0
        )
        
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning(f"Model {model_name} not found in tiktoken, falling back to cl100k_base.")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
        self.max_tokens = 128000
        self.reserve_tokens = 4000
        self.delimiter = "__DOCUCHAT_SOURCES_JSON__"

    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _truncate_tokens(self, text: str, max_tokens: int) -> str:
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.tokenizer.decode(tokens[:max_tokens])

    def _truncate_history(self, history: List[BaseMessage], limit: int) -> List[BaseMessage]:
        truncated = []
        current_tokens = 0
        for msg in reversed(history):
            msg_tokens = self._count_tokens(msg.content)
            if current_tokens + msg_tokens > limit:
                break
            truncated.insert(0, msg)
            current_tokens += msg_tokens
        return truncated

    async def get_chat_response(
        self, 
        query: str, 
        history: List[Dict[str, str]], 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            context_parts = []
            available_sources = []
            for chunk in context_chunks:
                meta = chunk.get("metadata", {})
                source_info = {
                    "document_name": meta.get("document_name", "Unknown"),
                    "page_number": meta.get("page_number", "N/A")
                }
                available_sources.append(source_info)
                context_parts.append(f"Source: {source_info['document_name']} (Page {source_info['page_number']})\nContent: {chunk.get('text', '')}")

            full_context_text = "\n\n---\n\n".join(context_parts)

            query_tokens = self._count_tokens(query)
            remaining_budget = self.max_tokens - self.reserve_tokens - query_tokens
            context_budget = int(remaining_budget * 0.7)
            history_budget = remaining_budget - context_budget

            truncated_context = self._truncate_tokens(full_context_text, context_budget)

            chat_history: List[BaseMessage] = []
            for msg in history:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))
            
            truncated_history = self._truncate_history(chat_history, history_budget)

            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are DocuChat AI, a professional assistant. "
                    "Use the provided context to answer the user's question accurately. "
                    "If the answer is not in the context, state that you do not have enough information. "
                    "Always cite sources in the text like [Document Name, Page X]. "
                    f"After your response, append the delimiter '{self.delimiter}' "
                    "followed by a JSON list of the sources you actually used to construct the answer. "
                    "Example: [{\"document_name\": \"Doc.pdf\", \"page_number\": 1}]"
                )),
                MessagesPlaceholder(variable_name="history"),
                ("human", f"Context:\n{truncated_context}\n\nQuestion: {query}")
            ])

            chain = prompt | self.llm
            response = await chain.ainvoke({"history": truncated_history})
            full_response = response.content

            parts = full_response.split(self.delimiter)
            answer = parts[0].strip()
            final_sources = []

            if len(parts) > 1:
                try:
                    json_str = parts[1].strip()
                    final_sources = json.loads(json_str)
                except json.JSONDecodeError:
                    seen = set()
                    for s in available_sources:
                        identifier = f"{s['document_name']}-{s['page_number']}"
                        if identifier not in seen:
                            final_sources.append(s)
                            seen.add(identifier)

            return {
                "answer": answer,
                "sources": final_sources
            }

        except Exception as e:
            logger.error(f"Error in LLMService: {str(e)}", exc_info=True)
            return {
                "answer": "I encountered an error while processing your request.",
                "sources": []
            }
