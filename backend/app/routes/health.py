"""GET /health — basic liveness and configuration check."""

from fastapi import APIRouter

from app.config.settings import settings
from app.rag.vector_store import get_collection_document_count
from app.schemas.api_schemas import HealthResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    try:
        indexed_count = get_collection_document_count()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read vector store document count: %s", exc)
        indexed_count = 0

    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        environment=settings.APP_ENV,
        google_api_key_configured=bool(settings.GOOGLE_API_KEY),
        knowledge_base_indexed_documents=indexed_count,
    )
