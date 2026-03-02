import uuid
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.models.schemas import Citation

class RAGEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def _get_vectorstore(self, session_id: str):
        return Chroma(
            collection_name=f"session_{session_id}",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )

    async def process_and_store_document(self, session_id: str, pages_data: List[Dict], filename: str):
        documents = []
        doc_id = str(uuid.uuid4())
        
        for page in pages_data:
            chunks = self.text_splitter.split_text(page["text"])
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": doc_id,
                        "filename": filename,
                        "page_number": page["page_number"],
                        "session_id": session_id
                    }
                ))
        
        vectorstore = self._get_vectorstore(session_id)
        vectorstore.add_documents(documents)
        return doc_id

    async def get_answer(self, session_id: str, query: str):
        vectorstore = self._get_vectorstore(session_id)
        # Retrieve top 5 chunks
        docs = vectorstore.similarity_search(query, k=5)
        
        if not docs:
            return "The answer was not found in the uploaded documents.", []

        context = "\n\n".join([f"Source: {d.metadata['filename']}, Page: {d.metadata['page_number']}\nContent: {d.page_content}" for d in docs])
        
        prompt = ChatPromptTemplate.from_template("""
        You are a document assistant. Answer the user's question based ONLY on the provided context. 
        If the answer is not in the context, say "The answer was not found in the uploaded documents."
        For every claim, cite the [Source Name] and [Page Number].

        Context:
        {context}

        Question: {query}
        """)
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context, "query": query})
        
        citations = []
        seen_citations = set()
        for d in docs:
            cit_key = (d.metadata['filename'], d.metadata['page_number'])
            if cit_key not in seen_citations:
                citations.append(Citation(
                    document_name=d.metadata['filename'],
                    page=d.metadata['page_number']
                ))
                seen_citations.add(cit_key)

        return response.content, citations

    async def delete_document(self, session_id: str, doc_id: str):
        vectorstore = self._get_vectorstore(session_id)
        # Chroma doesn't have a direct 'delete by metadata' in the LangChain wrapper easily
        # but we can access the underlying collection
        collection = vectorstore._collection
        collection.delete(where={"doc_id": doc_id})

    async def clear_session(self, session_id: str):
        vectorstore = self._get_vectorstore(session_id)
        vectorstore.delete_collection()
