import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class VectorStoreService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.persist_directory = "./chroma_db"
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        self.vector_store.add_documents(documents)

    def search(self, query: str, session_id: str, k: int = 5):
        # Metadata filtering for session isolation
        return self.vector_store.similarity_search(
            query, 
            k=k, 
            filter={"session_id": session_id}
        )

    def delete_session_docs(self, session_id: str, file_id: Optional[str] = None):
        # ChromaDB filtering for deletion
        where_filter = {"session_id": session_id}
        if file_id:
            where_filter["file_id"] = file_id
        
        # Note: LangChain's Chroma wrapper has limited delete support by filter in some versions
        # This is a simplified representation
        self.vector_store.delete(where=where_filter)

    def list_session_files(self, session_id: str):
        results = self.vector_store.get(where={"session_id": session_id})
        metadatas = results.get("metadatas", [])
        
        unique_files = {}
        for meta in metadatas:
            if meta["file_id"] not in unique_files:
                unique_files[meta["file_id"]] = meta["file_name"]
        
        return unique_files
