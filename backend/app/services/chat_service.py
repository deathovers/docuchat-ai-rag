from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.services.vector_store import VectorStoreService
from app.models.schemas import ChatResponse, Source

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.vector_store = VectorStoreService()

    async def get_chat_response(self, session_id: str, query: str) -> ChatResponse:
        # 1. Retrieve relevant chunks with session isolation
        docs = self.vector_store.search(query, session_id, k=6)
        
        if not docs:
            return ChatResponse(
                answer="The answer was not found in the uploaded documents.",
                sources=[]
            )

        context_text = "\n\n".join([
            f"Source: {d.metadata['file_name']}, Page: {d.metadata['page_number']}\nContent: {d.page_content}"
            for d in docs
        ])

        # 2. Construct strict grounding prompt
        system_prompt = (
            "You are an assistant that answers questions strictly based on the provided context. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Do not use outside knowledge. Always cite your sources by mentioning the filename and page."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Context:\n{context}\n\nQuestion: {query}")
        ])

        # 3. Generate response
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context_text, "query": query})
        
        # 4. Extract unique sources from retrieved documents
        sources = []
        seen_sources = set()
        for d in docs:
            source_key = (d.metadata['file_name'], d.metadata['page_number'])
            if source_key not in seen_sources:
                sources.append(Source(
                    file_name=d.metadata['file_name'],
                    page=d.metadata['page_number']
                ))
                seen_sources.add(source_key)

        return ChatResponse(answer=response.content, sources=sources)
