"""
Tool Agent.

Communicates with MCP tools (app/mcp/) on behalf of the workflow. Given
the classified emergency type, decides which real-world tools are
relevant (e.g. Fire -> nearest fire station, Medical -> nearest
hospital) and calls them, so the Planning and Report Generator agents
have concrete resource information instead of vague advice.

Runs between RAG Retrieval and Planning in the graph.
"""

from typing import Dict, List

from app.config.settings import settings
from app.mcp.registry import call_tool
from app.models.state import GuardianState
from app.utils.logger import get_logger

logger = get_logger(__name__)

AGENT_NAME = "tool_agent"

# Which MCP tools are relevant for each emergency category.
_TOOLS_BY_EMERGENCY_TYPE: Dict[str, List[str]] = {
    "Fire": ["fire_station_finder_tool", "emergency_contacts_tool", "weather_tool"],
    "Flood": ["weather_tool", "emergency_contacts_tool"],
    "Earthquake": ["emergency_contacts_tool", "hospital_finder_tool"],
    "Medical": ["hospital_finder_tool", "emergency_contacts_tool"],
    "Chemical Leak": ["hospital_finder_tool", "fire_station_finder_tool", "emergency_contacts_tool"],
    "Electrical": ["fire_station_finder_tool", "emergency_contacts_tool"],
    "Explosion": ["fire_station_finder_tool", "hospital_finder_tool", "emergency_contacts_tool"],
    "Road Accident": ["hospital_finder_tool", "police_finder_tool", "emergency_contacts_tool"],
    "Violence": ["police_finder_tool", "emergency_contacts_tool"],
    "Other": ["emergency_contacts_tool"],
}


def run_tool_agent(state: GuardianState) -> GuardianState:
    """
    Call the MCP tools relevant to the classified emergency type.

    Reads: state["emergency_type"], state["location"], state["country"]
    Writes: state["mcp_tool_results"]
    """
    emergency_type = state.get("emergency_type", "Other")
    location = state.get("location") or "the reported location"
    country = state.get("country") or settings.DEFAULT_EMERGENCY_COUNTRY

    tool_names = _TOOLS_BY_EMERGENCY_TYPE.get(emergency_type, ["emergency_contacts_tool"])
    logger.info("Tool agent calling %s for emergency_type='%s'", tool_names, emergency_type)

    results = []
    for tool_name in tool_names:
        if tool_name == "emergency_contacts_tool":
            result = call_tool(tool_name, country=country)
        elif tool_name == "weather_tool":
            result = call_tool(tool_name, location=location)
        else:
            # hospital_finder_tool, police_finder_tool, fire_station_finder_tool
            result = call_tool(tool_name, location=location)

        if not result.success:
            logger.warning("MCP tool '%s' failed: %s", tool_name, result.error)

        results.append(
            {
                "tool_name": result.tool_name,
                "success": result.success,
                "is_live": result.is_live,
                "data": result.data,
                "error": result.error,
            }
        )

    return {**state, "mcp_tool_results": results}
