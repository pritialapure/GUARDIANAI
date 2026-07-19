"""GET /documents — knowledge base indexing status."""

from fastapi import APIRouter

from app.schemas.api_schemas import DocumentsResponse
from app.services.documents_service import get_documents_status
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=DocumentsResponse)
async def documents() -> DocumentsResponse:
    """Return indexed vs. pending PDFs, for the dashboard's Knowledge Base Status panel."""
    return get_documents_status()
