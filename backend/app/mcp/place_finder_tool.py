"""
Generic "nearest facility" MCP tool base.

Hospital Finder, Police Station Finder, and Fire Station Finder all
share the same shape: given a location and a facility type, return
nearby facilities with name, address, distance, and contact info.
Subclasses just set `place_type`, `name`, and `description`.

Real implementation point: Google Places Text Search API (or any
similar provider) keyed by MAPS_API_KEY. Falls back to structured
placeholder data when no key is configured.
"""

import requests

from app.config.settings import settings
from app.mcp.base import MCPTool, MCPToolResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PlaceFinderTool(MCPTool):
    place_type: str = "point_of_interest"

    def _placeholder_data(self, location: str) -> dict:
        return {
            "location": location,
            "facilities": [
                {
                    "name": f"Nearest {self.place_type.replace('_', ' ')} (placeholder)",
                    "address": "Configure MAPS_API_KEY for real results",
                    "distance_km": None,
                    "phone": None,
                }
            ],
            "note": "Placeholder data — configure MAPS_API_KEY for live nearby-facility search.",
        }

    def execute(self, location: str, radius_km: float = 5.0, **kwargs) -> MCPToolResult:
        if not settings.MAPS_API_KEY:
            logger.info("MAPS_API_KEY not set — returning placeholder %s data.", self.place_type)
            return MCPToolResult(
                tool_name=self.name, success=True, is_live=False, data=self._placeholder_data(location)
            )

        # Real implementation point: Google Places Text Search (or equivalent).
        response = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                "query": f"{self.place_type} near {location}",
                "radius": radius_km * 1000,
                "key": settings.MAPS_API_KEY,
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])[:5]

        facilities = [
            {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating"),
                "phone": None,  # requires a separate Place Details call
            }
            for place in results
        ]

        return MCPToolResult(
            tool_name=self.name,
            success=True,
            is_live=True,
            data={"location": location, "facilities": facilities},
        )


class HospitalFinderTool(PlaceFinderTool):
    name = "hospital_finder_tool"
    description = "Find the nearest hospitals to a given location."
    place_type = "hospital"


class PoliceFinderTool(PlaceFinderTool):
    name = "police_finder_tool"
    description = "Find the nearest police stations to a given location."
    place_type = "police station"


class FireStationFinderTool(PlaceFinderTool):
    name = "fire_station_finder_tool"
    description = "Find the nearest fire stations to a given location."
    place_type = "fire station"
