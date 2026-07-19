"""
ChromaDB vector store access for the Guardian Council AI knowledge base.

A single persisted Chroma collection backs the whole application.
Every other module (ingestion, retriever) goes through
`get_vector_store()` so there is exactly one place that knows about
Chroma's constructor arguments.
"""

import time
from functools import lru_cache
from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.rag.embeddings import get_embedding_function
from app.utils.exceptions import RetrievalError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_vector_store() -> Chroma:
    """Return the (cached) persisted Chroma vector store instance."""
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=str(persist_dir),
    )


def _batched(items: List[Document], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=30, max=90),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _add_batch_with_retry(store: Chroma, batch: List[Document]) -> List[str]:
    """Embed+add one batch, retrying with backoff if the embedding API rate-limits us."""
    return store.add_documents(documents=batch)


def add_documents_to_store(chunks: List[Document]) -> List[str]:
    """
    Embed and persist document chunks in rate-limit-safe batches.

    Free-tier Gemini embedding quotas are commonly capped around 100
    requests/minute. Sending hundreds of chunks in a single call triggers
    a 429. This batches chunks (settings.EMBEDDING_BATCH_SIZE per batch)
    and pauses between batches (settings.EMBEDDING_BATCH_DELAY_SECONDS)
    to stay under that limit, with exponential-backoff retry as a safety
    net if a batch still gets rate-limited.
    """
    if not chunks:
        return []

    store = get_vector_store()
    batches = list(_batched(chunks, settings.EMBEDDING_BATCH_SIZE))
    all_ids: List[str] = []

    for batch_index, batch in enumerate(batches, start=1):
        logger.info(
            "Embedding batch %d/%d (%d chunks)...", batch_index, len(batches), len(batch)
        )
        try:
            ids = _add_batch_with_retry(store, batch)
        except Exception as exc:  # noqa: BLE001
            if all_ids:
                logger.warning(
                    "Batch %d/%d failed — rolling back %d chunk(s) already added for this "
                    "file so it isn't left partially indexed.",
                    batch_index,
                    len(batches),
                    len(all_ids),
                )
                try:
                    store.delete(ids=all_ids)
                except Exception as rollback_exc:  # noqa: BLE001
                    logger.error("Rollback also failed: %s", rollback_exc)
            raise RetrievalError(f"Failed to add documents to vector store: {exc}") from exc

        all_ids.extend(ids)

        is_last_batch = batch_index == len(batches)
        is_rate_limited_provider = settings.EMBEDDING_PROVIDER.lower() == "gemini"
        if not is_last_batch and is_rate_limited_provider:
            logger.info(
                "Pausing %.0fs before next batch to respect embedding API rate limits...",
                settings.EMBEDDING_BATCH_DELAY_SECONDS,
            )
            time.sleep(settings.EMBEDDING_BATCH_DELAY_SECONDS)

    logger.info("Added %d chunks to collection '%s'", len(all_ids), settings.CHROMA_COLLECTION_NAME)
    return all_ids


def get_indexed_source_files() -> List[str]:
    """Return the distinct source PDF filenames currently indexed in the vector store."""
    store = get_vector_store()
    try:
        record = store.get(include=["metadatas"])
    except Exception as exc:  # noqa: BLE001
        raise RetrievalError(f"Failed to read vector store metadata: {exc}") from exc

    sources = {
        meta.get("source_file")
        for meta in record.get("metadatas", [])
        if meta and meta.get("source_file")
    }
    return sorted(sources)


def get_collection_document_count() -> int:
    """Return the total number of chunks currently stored in the collection."""
    store = get_vector_store()
    try:
        return store._collection.count()  # noqa: SLF001 - Chroma has no public count() API
    except Exception as exc:  # noqa: BLE001
        raise RetrievalError(f"Failed to count vector store documents: {exc}") from exc
