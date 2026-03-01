from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from app.core.config import settings
import os

class RAGEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=self.embeddings,
            collection_name=settings.COLLECTION_NAME
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        # In-memory session memory storage for MVP
        self.memories = {}

    def add_documents(self, documents):
        self.vector_store.add_documents(documents)

    def get_session_memory(self, session_id: str):
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
                k=5
            )
        return self.memories[session_id]

    async def chat(self, session_id: str, query: str):
        # Filter by session_id to ensure data isolation
        retriever = self.vector_store.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}, "k": 5}
        )

        memory = self.get_session_memory(session_id)
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True
        )

        # System prompt is handled via the chain's default or can be customized
        # For MVP, we use the default and rely on the prompt instructions in the TRD
        # by wrapping the query if needed, but ConversationalRetrievalChain is robust.
        
        response = await chain.ainvoke({"question": query})
        
        answer = response["answer"]
        source_documents = response["source_documents"]
        
        sources = []
        seen_sources = set()
        for doc in source_documents:
            src_key = f"{doc.metadata['source']}_{doc.metadata['page']}"
            if src_key not in seen_sources:
                sources.append({
                    "file": doc.metadata["source"],
                    "page": doc.metadata["page"]
                })
                seen_sources.add(src_key)
                
        return answer, sources
