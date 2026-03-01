from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "your-openai-api-key"
    CHROMA_DB_DIR: str = "./chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    COLLECTION_NAME: str = "docuchat_collection"

    class Config:
        env_file = ".env"

settings = Settings()
