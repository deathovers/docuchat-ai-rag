from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from app.core.config import settings
from typing import List, Dict, Any

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

def get_vectorstore():
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    return LangChainPinecone(index, embeddings, "text")

def upsert_documents(documents):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)

def query_documents(query: str, session_id: str, k: int = 5) -> List[Dict[str, Any]]:
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(
        query, 
        k=k, 
        filter={"session_id": session_id}
    )
    
    return [
        {
            "text": doc.page_content,
            "file_name": doc.metadata["file_name"],
            "page_number": doc.metadata["page_number"]
        }
        for doc in results
    ]

def delete_session_vectors(session_id: str):
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    index.delete(filter={"session_id": session_id})

def delete_file_vectors(session_id: str, file_name: str):
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    index.delete(filter={"session_id": session_id, "file_name": file_name})
