"""POST /chat — run one conversation turn through the multi-agent workflow."""

from fastapi import APIRouter

from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat_message
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to Guardian Council AI.

    Reuse the same `thread_id` across requests to continue a conversation;
    the checkpointer restores prior context automatically.
    """
    logger.info("POST /chat thread_id='%s'", request.thread_id)
    return handle_chat_message(request)
