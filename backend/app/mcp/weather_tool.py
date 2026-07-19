"""
Weather MCP Tool.

Returns current weather conditions for a location — relevant to fire
spread risk, flood severity, or road accident visibility. Uses a real
API when WEATHER_API_KEY is configured; otherwise returns clearly
labeled placeholder data with the same shape so downstream code never
has to special-case "no API key" logic.
"""

import requests

from app.config.settings import settings
from app.mcp.base import MCPTool, MCPToolResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WeatherTool(MCPTool):
    name = "weather_tool"
    description = "Get current weather conditions for a location (temperature, wind, precipitation)."

    def execute(self, location: str, **kwargs) -> MCPToolResult:
        if not settings.WEATHER_API_KEY:
            logger.info("WEATHER_API_KEY not set — returning placeholder weather data.")
            return MCPToolResult(
                tool_name=self.name,
                success=True,
                is_live=False,
                data={
                    "location": location,
                    "condition": "unknown (placeholder — configure WEATHER_API_KEY for live data)",
                    "temperature_celsius": None,
                    "wind_speed_kmh": None,
                    "precipitation_mm": None,
                },
            )

        # Real implementation point: e.g. OpenWeatherMap current-weather endpoint.
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": settings.WEATHER_API_KEY, "units": "metric"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        return MCPToolResult(
            tool_name=self.name,
            success=True,
            is_live=True,
            data={
                "location": location,
                "condition": payload.get("weather", [{}])[0].get("description", "unknown"),
                "temperature_celsius": payload.get("main", {}).get("temp"),
                "wind_speed_kmh": payload.get("wind", {}).get("speed"),
                "precipitation_mm": payload.get("rain", {}).get("1h", 0),
            },
        )
