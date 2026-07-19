"""POST /ingest — ingest new PDFs from the knowledge_base/ directory into ChromaDB."""

from fastapi import APIRouter

from app.schemas.api_schemas import IngestRequest, IngestResponse
from app.services.ingestion_service import handle_ingest_request
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest = IngestRequest()) -> IngestResponse:
    """Ingest every PDF in knowledge_base/ that isn't already indexed."""
    logger.info("POST /ingest force=%s", request.force)
    return handle_ingest_request(force=request.force)
