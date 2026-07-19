"""
Maps / Directions MCP Tool.

Returns route and distance information between two points — used to
estimate responder ETA or evacuation routes. Real implementation point:
Google Directions API keyed by MAPS_API_KEY.
"""

import requests

from app.config.settings import settings
from app.mcp.base import MCPTool, MCPToolResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MapsTool(MCPTool):
    name = "maps_tool"
    description = "Get route distance and estimated travel time between two locations."

    def execute(self, origin: str, destination: str, **kwargs) -> MCPToolResult:
        if not settings.MAPS_API_KEY:
            logger.info("MAPS_API_KEY not set — returning placeholder route data.")
            return MCPToolResult(
                tool_name=self.name,
                success=True,
                is_live=False,
                data={
                    "origin": origin,
                    "destination": destination,
                    "distance_km": None,
                    "duration_minutes": None,
                    "note": "Placeholder data — configure MAPS_API_KEY for live routing.",
                },
            )

        response = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params={"origin": origin, "destination": destination, "key": settings.MAPS_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        routes = payload.get("routes", [])

        if not routes:
            return MCPToolResult(
                tool_name=self.name,
                success=False,
                is_live=True,
                error=f"No route found between '{origin}' and '{destination}'.",
            )

        leg = routes[0]["legs"][0]
        return MCPToolResult(
            tool_name=self.name,
            success=True,
            is_live=True,
            data={
                "origin": origin,
                "destination": destination,
                "distance_km": leg.get("distance", {}).get("value", 0) / 1000,
                "duration_minutes": leg.get("duration", {}).get("value", 0) / 60,
            },
        )
