import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuChat AI"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "docuchat")
    
    class Config:
        env_file = ".env"

settings = Settings()
