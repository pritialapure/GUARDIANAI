"""
Central application configuration.

All environment-driven settings for Guardian Council AI live here.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Strongly typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================================
    # Application
    # ==========================================================
    APP_NAME: str = "Guardian Council AI"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # CORS
    # ==========================================================
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ==========================================================
    # Google Gemini
    # ==========================================================
    GOOGLE_API_KEY: str = ""

    # Chat Model
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"

    # Embedding Model
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # Use Gemini embeddings
    EMBEDDING_PROVIDER: str = "huggingface"

    # ==========================================================
    # Chroma Vector Store
    # ==========================================================
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "guardian_council_knowledge_base"
    KNOWLEDGE_BASE_DIR: str = str(BASE_DIR / "knowledge_base")

    # ==========================================================
    # Text Splitting
    # ==========================================================
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 4

    # ==========================================================
    # Embedding Batch Settings
    # ==========================================================
    EMBEDDING_BATCH_SIZE: int = 10
    EMBEDDING_BATCH_DELAY_SECONDS: float = 2.0

    # ==========================================================
    # Optional APIs
    # ==========================================================
    TAVILY_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    MAPS_API_KEY: str = ""
    HOSPITAL_FINDER_API_KEY: str = ""
    DEFAULT_EMERGENCY_COUNTRY: str = "united states"

    # ==========================================================
    # Memory
    # ==========================================================
    MEMORY_BACKEND: str = "in_memory"
    SQLITE_MEMORY_PATH: str = str(BASE_DIR / "memory_store.sqlite")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()