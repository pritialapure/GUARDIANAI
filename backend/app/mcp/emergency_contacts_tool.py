"""
Emergency Contacts MCP Tool.

Returns the correct emergency phone numbers for a given country. Unlike
the other tools, this doesn't need a paid API — emergency numbers are
public, stable data — but is still structured as an MCPTool so the Tool
Agent can call it uniformly alongside the others, and so a live
API/database can replace `_CONTACTS_BY_COUNTRY` later without touching
any calling code.
"""

from app.mcp.base import MCPTool, MCPToolResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

_CONTACTS_BY_COUNTRY = {
    "united states": {"police": "911", "fire": "911", "medical": "911", "general": "911"},
    "india": {"police": "100", "fire": "101", "medical": "102", "general": "112"},
    "united kingdom": {"police": "999", "fire": "999", "medical": "999", "general": "112"},
    "european union": {"police": "112", "fire": "112", "medical": "112", "general": "112"},
    "australia": {"police": "000", "fire": "000", "medical": "000", "general": "000"},
    "canada": {"police": "911", "fire": "911", "medical": "911", "general": "911"},
}

_DEFAULT_CONTACT = {"general": "112", "note": "112 works as a fallback emergency number in most countries."}


class EmergencyContactsTool(MCPTool):
    name = "emergency_contacts_tool"
    description = "Get the correct emergency phone numbers (police, fire, medical) for a country."

    def execute(self, country: str, **kwargs) -> MCPToolResult:
        key = country.strip().lower()
        contacts = _CONTACTS_BY_COUNTRY.get(key)

        if contacts is None:
            logger.warning("No emergency contact data for '%s' — returning global fallback.", country)
            return MCPToolResult(
                tool_name=self.name,
                success=True,
                is_live=False,
                data={"country": country, "contacts": _DEFAULT_CONTACT},
            )

        return MCPToolResult(
            tool_name=self.name,
            success=True,
            is_live=True,
            data={"country": country, "contacts": contacts},
        )
