"""
Chat service.

Thin business-logic layer between the /chat route and
app.graph.workflow. Keeping this separate from the route means the
route file only handles HTTP concerns (validation, status codes) while
this handles orchestration concerns.
"""

from app.graph.workflow import invoke_workflow
from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.utils.exceptions import AgentExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def handle_chat_message(request: ChatRequest) -> ChatResponse:
    """Run one conversation turn through the multi-agent workflow and shape the API response."""
    try:
        result = invoke_workflow(
            user_query=request.message,
            thread_id=request.thread_id,
            location=request.location or "",
            country=request.country or "",
        )
    except AgentExecutionError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AgentExecutionError(str(exc), agent_name="workflow") from exc

    return ChatResponse(
        thread_id=request.thread_id,
        response=result.get("final_response", ""),
        requires_emergency_workflow=result.get("requires_emergency_workflow", False),
        emergency_type=result.get("emergency_type"),
        classification_confidence=result.get("classification_confidence"),
        action_plan=result.get("action_plan"),
        validation_passed=result.get("validation_passed"),
        unsupported_claims=result.get("unsupported_claims", []),
        source_references=result.get("source_references", []),
        mcp_tool_results=result.get("mcp_tool_results", []),
        final_report=result.get("final_report"),
    )
