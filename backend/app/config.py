from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "sqlite:///./legal_app.db"

    # --- JWT ---
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- Google Gemini ---
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "legal_documents"

    # --- Embedding ---
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"

    # --- RAG ---
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 80
    TOP_K_RESULTS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.65

    # --- Rate Limiting ---
    GEMINI_REQUESTS_PER_MINUTE: int = 15
    GEMINI_REQUESTS_PER_DAY: int = 1500

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # --- App ---
    APP_NAME: str = "Legal AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
