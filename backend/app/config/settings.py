"""
Central application configuration.

All environment-driven settings for Guardian Council AI live here.
Uses pydantic-settings so values are validated at startup and every
other module imports a single shared `settings` instance instead of
calling `os.getenv` directly.
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

    # --- Application ---
    APP_NAME: str = "Guardian Council AI"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Google Gemini ---
    GOOGLE_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # --- Embeddings fallback (in case Gemini embeddings are unavailable) ---
    EMBEDDING_PROVIDER: str = "gemini"  # "gemini" | "huggingface"
    HUGGINGFACE_EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"

    # --- Vector Store ---
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "guardian_council_knowledge_base"
    KNOWLEDGE_BASE_DIR: str = str(BASE_DIR / "knowledge_base")

    # --- Chunking ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 4

    # Free-tier Gemini embedding quota is commonly 100 requests/minute.
    # Ingestion batches chunks and pauses between batches to stay under it.
    EMBEDDING_BATCH_SIZE: int = 90
    EMBEDDING_BATCH_DELAY_SECONDS: float = 61.0

    # --- Tavily (optional web search augmentation) ---
    TAVILY_API_KEY: str = ""

    # --- MCP / External Tool Placeholders ---
    WEATHER_API_KEY: str = ""
    MAPS_API_KEY: str = ""
    HOSPITAL_FINDER_API_KEY: str = ""
    DEFAULT_EMERGENCY_COUNTRY: str = "united states"

    # --- Memory ---
    MEMORY_BACKEND: str = "in_memory"  # "in_memory" | "sqlite"
    SQLITE_MEMORY_PATH: str = str(BASE_DIR / "memory_store.sqlite")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()


settings = get_settings()
