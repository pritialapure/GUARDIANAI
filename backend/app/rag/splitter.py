"""
Chunking for the Guardian Council AI knowledge base.

Wraps RecursiveCharacterTextSplitter so chunk size/overlap are driven
by settings rather than hardcoded, and every chunk gets a stable
chunk_id in its metadata for citation and validation downstream.
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Build a RecursiveCharacterTextSplitter configured from settings."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        add_start_index=True,
    )


def split_documents(documents: List[Document]) -> List[Document]:
    """Split loaded documents into retrieval-sized chunks with stable IDs."""
    if not documents:
        return []

    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        source = chunk.metadata.get("source_file", "unknown")
        page = chunk.metadata.get("page", 0)
        chunk.metadata["chunk_id"] = f"{source}-p{page}-c{index}"

    logger.info(
        "Split %d document(s) into %d chunks (size=%d, overlap=%d)",
        len(documents),
        len(chunks),
        settings.CHUNK_SIZE,
        settings.CHUNK_OVERLAP,
    )
    return chunks
