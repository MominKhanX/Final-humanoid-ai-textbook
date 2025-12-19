"""
Configuration management for RAG Chatbot Backend
Loads environment variables and provides typed settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # FastEmbed Configuration (FREE, Local, No API!)
    fastembed_model: str = "BAAI/bge-small-en-v1.5"  # 384-dim, fast, high quality

    # Google Gemini Configuration (FREE LLM for Chat!)
    gemini_api_key: str
    gemini_chat_model: str = "gemini-1.5-flash"  # Fast, free, high quality
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 2048

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "textbook_chunks"
    qdrant_vector_size: int = 384  # FastEmbed BAAI/bge-small-en-v1.5 dimension

    # Neon Postgres Configuration
    database_url: str

    # Frontend Configuration
    frontend_url: str

    # Rate Limiting
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # RAG Configuration
    rag_top_k: int = 5  # Number of chunks to retrieve
    rag_relevance_threshold: float = 0.7  # Minimum similarity score

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
