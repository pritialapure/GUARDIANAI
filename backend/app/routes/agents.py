"""GET /agents — list all agents in the workflow and all registered MCP tools."""

from fastapi import APIRouter

from app.schemas.api_schemas import AgentsResponse
from app.services.agent_status_service import get_agents_status
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["agents"])


@router.get("/agents", response_model=AgentsResponse)
async def agents() -> AgentsResponse:
    """Return metadata for every agent and MCP tool, for the dashboard's Agent Status panel."""
    return get_agents_status()
