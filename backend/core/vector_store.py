import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

class VectorStoreManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            client=self.client,
            collection_name="docuchat_collection",
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        self.vector_store.add_documents(documents)

    def get_retriever(self, session_id: str):
        return self.vector_store.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}, "k": 5}
        )

    def delete_by_file_id(self, session_id: str, file_id: str):
        # ChromaDB direct deletion via metadata filter is slightly complex in LangChain wrapper
        # We use the underlying client for precise deletion
        collection = self.client.get_collection("docuchat_collection")
        collection.delete(where={"$and": [{"session_id": session_id}, {"file_id": file_id}]})
