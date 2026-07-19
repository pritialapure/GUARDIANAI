"""
Base MCP tool interface.

Every tool in app/mcp/ implements this contract so the Tool Agent can
call any of them uniformly, and so real APIs can be swapped in later
without touching the agent that calls them. Each tool reports whether
it's running against a real API or placeholder data via `is_live`, so
the frontend/report can be transparent about data source.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MCPToolResult:
    """Standard result envelope returned by every MCP tool."""

    tool_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    is_live: bool = False  # False = placeholder/mock data, True = real API response
    error: str = ""


class MCPTool(ABC):
    """Abstract base class for all MCP-compatible emergency tools."""

    name: str = "base_tool"
    description: str = "Base MCP tool. Override in subclasses."

    @abstractmethod
    def execute(self, **kwargs) -> MCPToolResult:
        """Run the tool and return a standardized MCPToolResult."""
        raise NotImplementedError

    def safe_execute(self, **kwargs) -> MCPToolResult:
        """Wrap execute() so a single tool failure never crashes the caller."""
        try:
            return self.execute(**kwargs)
        except Exception as exc:  # noqa: BLE001
            return MCPToolResult(tool_name=self.name, success=False, error=str(exc))
