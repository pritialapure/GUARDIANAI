"""
MCP tool registry.

Single source of truth mapping tool name -> tool instance. The Tool
Agent and the /agents status API route both go through this registry
instead of importing individual tool classes directly, so adding a new
MCP tool later means registering it here once.
"""

from typing import Dict, List

from app.mcp.base import MCPTool, MCPToolResult
from app.mcp.emergency_contacts_tool import EmergencyContactsTool
from app.mcp.gps_location_tool import GPSLocationTool
from app.mcp.maps_tool import MapsTool
from app.mcp.place_finder_tool import FireStationFinderTool, HospitalFinderTool, PoliceFinderTool
from app.mcp.weather_tool import WeatherTool

_REGISTRY: Dict[str, MCPTool] = {
    tool.name: tool
    for tool in [
        WeatherTool(),
        HospitalFinderTool(),
        PoliceFinderTool(),
        FireStationFinderTool(),
        MapsTool(),
        EmergencyContactsTool(),
        GPSLocationTool(),
    ]
}


def get_tool(tool_name: str) -> MCPTool:
    """Look up a registered MCP tool by name. Raises KeyError if not found."""
    if tool_name not in _REGISTRY:
        raise KeyError(f"Unknown MCP tool '{tool_name}'. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[tool_name]


def list_tools() -> List[dict]:
    """Return metadata for every registered tool (used by GET /agents)."""
    return [{"name": tool.name, "description": tool.description} for tool in _REGISTRY.values()]


def call_tool(tool_name: str, **kwargs) -> MCPToolResult:
    """Convenience helper: look up and safely execute a tool in one call."""
    tool = get_tool(tool_name)
    return tool.safe_execute(**kwargs)
