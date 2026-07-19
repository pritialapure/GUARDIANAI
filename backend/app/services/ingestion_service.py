"""
Ingestion service — thin wrapper around app.rag.ingestion for the /ingest route.
"""

from app.rag.ingestion import ingest_knowledge_base
from app.schemas.api_schemas import IngestResponse


def handle_ingest_request(force: bool = False) -> IngestResponse:
    """Run the knowledge base ingestion pipeline and shape the API response."""
    summary = ingest_knowledge_base(force=force)
    return IngestResponse(
        newly_ingested_files=summary.newly_ingested_files,
        skipped_already_indexed=summary.skipped_already_indexed,
        failed_files=summary.failed_files,
        total_chunks_added=summary.total_chunks_added,
    )
