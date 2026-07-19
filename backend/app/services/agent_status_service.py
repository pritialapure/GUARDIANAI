"""
Agent status service — powers GET /agents.

Agent descriptions are static metadata (there's no runtime "agent
registry" object the way there is for MCP tools, since agents are plain
functions in the LangGraph workflow). MCP tool info comes live from the
MCP registry so it always reflects what's actually available.
"""

from app.mcp.registry import list_tools
from app.schemas.api_schemas import AgentInfo, AgentsResponse, MCPToolInfo

_AGENTS = [
    AgentInfo(name="coordinator_agent", role="Decides whether the message needs the full emergency workflow."),
    AgentInfo(name="classification_agent", role="Classifies the emergency into one of 10 categories."),
    AgentInfo(name="rag_retrieval_agent", role="Retrieves trusted context from the knowledge base."),
    AgentInfo(name="tool_agent", role="Calls relevant MCP tools (hospitals, stations, weather, contacts)."),
    AgentInfo(name="planning_agent", role="Generates a structured, grounded emergency action plan."),
    AgentInfo(name="validation_agent", role="Verifies every plan recommendation is backed by retrieved context."),
    AgentInfo(name="report_generator_agent", role="Produces the final structured incident report."),
    AgentInfo(name="memory_agent", role="Maintains rolling conversation history."),
    AgentInfo(name="simple_response_agent", role="Handles greetings and non-emergency messages directly."),
]


def get_agents_status() -> AgentsResponse:
    """Return static agent metadata plus the live MCP tool registry."""
    mcp_tools = [MCPToolInfo(name=tool["name"], description=tool["description"]) for tool in list_tools()]
    return AgentsResponse(agents=_AGENTS, mcp_tools=mcp_tools)
