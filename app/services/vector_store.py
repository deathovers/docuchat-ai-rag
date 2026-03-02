import chromadb
from chromadb.utils import embedding_functions
from app.config import settings
from typing import List, Dict
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name="docuchat_collection",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: List[Dict], session_id: str, file_id: str):
        ids = [str(uuid.uuid4()) for _ in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = []
        for c in chunks:
            meta = c["metadata"].copy()
            meta["session_id"] = session_id
            meta["file_id"] = file_id
            metadatas.append(meta)
            
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def query(self, query_text: str, session_id: str, k: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=k,
            where={"session_id": session_id}
        )
        
        formatted_results = []
        if results["documents"]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
        return formatted_results

    def delete_file_vectors(self, session_id: str, file_id: str):
        self.collection.delete(
            where={"$and": [{"session_id": session_id}, {"file_id": file_id}]}
        )

    def clear_session_vectors(self, session_id: str):
        self.collection.delete(
            where={"session_id": session_id}
        )
