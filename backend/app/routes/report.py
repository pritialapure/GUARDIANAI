"""POST /report — retrieve the final incident report for a completed conversation thread."""

from fastapi import APIRouter

from app.schemas.api_schemas import ReportRequest, ReportResponse
from app.services.report_service import get_report_for_thread
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["report"])


@router.post("/report", response_model=ReportResponse)
async def report(request: ReportRequest) -> ReportResponse:
    """Fetch the incident report generated during a prior /chat call on this thread_id."""
    logger.info("POST /report thread_id='%s'", request.thread_id)
    final_report = get_report_for_thread(request.thread_id)
    return ReportResponse(thread_id=request.thread_id, final_report=final_report)
