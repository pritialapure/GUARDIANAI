"""
Embedding layer for Guardian Council AI.

Uses Google Gemini embeddings only.
"""

from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config.settings import settings
from app.utils.exceptions import ConfigurationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_embedding_function():
    """
    Return the Gemini embedding model.
    Cached so it is initialized only once.
    """

    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError("GOOGLE_API_KEY is missing.")

    logger.info(
        "Using Gemini embeddings: %s",
        settings.GEMINI_EMBEDDING_MODEL,
    )

    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )