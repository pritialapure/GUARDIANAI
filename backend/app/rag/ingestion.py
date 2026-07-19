"""
Ingestion pipeline for the Guardian Council AI knowledge base.

Orchestrates loader -> splitter -> vector_store so a new PDF dropped
into `knowledge_base/` can be indexed with zero code changes — just
call `ingest_knowledge_base()` (via the /ingest route or a script).

Already-indexed files are skipped on subsequent runs by checking
`source_file` metadata already present in the collection, so ingestion
is safe to re-run at any time (e.g. on every backend startup).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from app.rag.loader import list_knowledge_base_pdfs, load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import add_documents_to_store, get_indexed_source_files
from app.utils.exceptions import DocumentIngestionError, RetrievalError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class IngestionSummary:
    """Result of an ingestion run, returned to the /ingest API route."""

    newly_ingested_files: List[str]
    skipped_already_indexed: List[str]
    failed_files: List[str]
    total_chunks_added: int


def ingest_knowledge_base(force: bool = False) -> IngestionSummary:
    """
    Ingest every PDF in the knowledge base directory that isn't already indexed.

    Args:
        force: If True, re-ingest even files already present in the vector store
               (useful if a PDF was replaced with updated content but kept the
               same filename).
    """
    pdf_paths = list_knowledge_base_pdfs()
    if not pdf_paths:
        logger.warning("Knowledge base directory is empty — nothing to ingest.")
        return IngestionSummary([], [], [], 0)

    already_indexed = set(get_indexed_source_files()) if not force else set()

    newly_ingested: List[str] = []
    skipped: List[str] = []
    failed: List[str] = []
    total_chunks = 0

    for pdf_path in pdf_paths:
        if pdf_path.name in already_indexed:
            skipped.append(pdf_path.name)
            continue

        try:
            total_chunks += _ingest_single_file(pdf_path)
            newly_ingested.append(pdf_path.name)
        except (DocumentIngestionError, RetrievalError) as exc:
            logger.error("Ingestion failed for '%s': %s", pdf_path.name, exc.message)
            failed.append(pdf_path.name)

    logger.info(
        "Ingestion complete: %d new, %d skipped, %d failed, %d chunks added",
        len(newly_ingested),
        len(skipped),
        len(failed),
        total_chunks,
    )

    return IngestionSummary(
        newly_ingested_files=newly_ingested,
        skipped_already_indexed=skipped,
        failed_files=failed,
        total_chunks_added=total_chunks,
    )


def _ingest_single_file(pdf_path: Path) -> int:
    """Load, split, and embed a single PDF. Returns the number of chunks added."""
    pages = load_pdf(pdf_path)
    chunks = split_documents(pages)
    if not chunks:
        raise DocumentIngestionError(f"'{pdf_path.name}' produced no chunks after splitting.")

    ids = add_documents_to_store(chunks)
    return len(ids)
