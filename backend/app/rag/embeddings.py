"""
Embedding layer for Guardian Council AI.

Uses Hugging Face embeddings.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_embedding_function():
    """
    Return the Hugging Face embedding model.
    Cached so it is initialized only once.
    """

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    logger.info("Using HuggingFace embeddings: %s", model_name)

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )