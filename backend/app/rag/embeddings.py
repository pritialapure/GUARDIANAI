"""
Embedding layer for the Guardian Council AI knowledge base.

Preference is Gemini embeddings (`GEMINI_EMBEDDING_MODEL`). If
compatibility or quota issues arise, set EMBEDDING_PROVIDER=huggingface
in .env to swap to a local sentence-transformers model with zero other
code changes — every other RAG module only ever calls
`get_embedding_function()`.
"""

from functools import lru_cache
from typing import Any

from app.config.settings import settings
from app.utils.exceptions import ConfigurationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _build_gemini_embeddings() -> Any:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError(
            "GOOGLE_API_KEY is not set. Required for EMBEDDING_PROVIDER=gemini."
        )

    logger.info("Using Gemini embeddings: %s", settings.GEMINI_EMBEDDING_MODEL)
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def _build_huggingface_embeddings() -> Any:
    from langchain_huggingface import HuggingFaceEmbeddings

    logger.info("Using HuggingFace embeddings: %s", settings.HUGGINGFACE_EMBEDDING_MODEL)
    return HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)


@lru_cache
def get_embedding_function() -> Any:
    """
    Return the configured embedding function.

    Cached so the underlying model (Gemini client or local sentence-transformers
    model) is only initialized once per process.
    """
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "gemini":
        try:
            return _build_gemini_embeddings()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Gemini embeddings unavailable (%s). Falling back to HuggingFace.", exc
            )
            return _build_huggingface_embeddings()

    if provider == "huggingface":
        return _build_huggingface_embeddings()

    raise ConfigurationError(
        f"Unknown EMBEDDING_PROVIDER '{settings.EMBEDDING_PROVIDER}'. "
        "Use 'gemini' or 'huggingface'."
    )
