"""
GPS Location MCP Tool.

Resolves raw latitude/longitude coordinates (e.g. from a responder's
device or the frontend's browser geolocation API) into a human-readable
address via reverse geocoding. Real implementation point: Google
Geocoding API keyed by MAPS_API_KEY.
"""

import requests

from app.config.settings import settings
from app.mcp.base import MCPTool, MCPToolResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GPSLocationTool(MCPTool):
    name = "gps_location_tool"
    description = "Reverse-geocode GPS latitude/longitude coordinates into a readable address."

    def execute(self, latitude: float, longitude: float, **kwargs) -> MCPToolResult:
        if not settings.MAPS_API_KEY:
            logger.info("MAPS_API_KEY not set — returning placeholder reverse-geocode data.")
            return MCPToolResult(
                tool_name=self.name,
                success=True,
                is_live=False,
                data={
                    "latitude": latitude,
                    "longitude": longitude,
                    "address": "unknown (placeholder — configure MAPS_API_KEY for live reverse geocoding)",
                },
            )

        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{latitude},{longitude}", "key": settings.MAPS_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        address = results[0].get("formatted_address") if results else "Address not found"

        return MCPToolResult(
            tool_name=self.name,
            success=True,
            is_live=True,
            data={"latitude": latitude, "longitude": longitude, "address": address},
        )
