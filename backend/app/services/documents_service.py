"""
Documents service — powers GET /documents.

Reports which knowledge-base PDFs are indexed in ChromaDB versus which
are sitting in knowledge_base/ but haven't been ingested yet, so the
frontend's "Knowledge Base Status" panel can show an accurate picture.
"""

from app.rag.loader import list_knowledge_base_pdfs
from app.rag.vector_store import get_collection_document_count, get_indexed_source_files
from app.schemas.api_schemas import DocumentsResponse


def get_documents_status() -> DocumentsResponse:
    """Compare files on disk against what's indexed in the vector store."""
    indexed = set(get_indexed_source_files())
    on_disk = {path.name for path in list_knowledge_base_pdfs()}
    pending = sorted(on_disk - indexed)

    return DocumentsResponse(
        indexed_files=sorted(indexed),
        total_chunks=get_collection_document_count(),
        pending_files=pending,
    )
