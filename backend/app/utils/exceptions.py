"""
Custom exception hierarchy for Guardian Council AI.

Using typed exceptions (instead of raising bare Exception) lets the
FastAPI exception handlers in app/main.py return consistent, meaningful
error responses to the frontend.
"""


class GuardianCouncilError(Exception):
    """Base exception for all Guardian Council AI errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConfigurationError(GuardianCouncilError):
    """Raised when required configuration/environment variables are missing."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class DocumentIngestionError(GuardianCouncilError):
    """Raised when a document fails to load, split, or embed."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class RetrievalError(GuardianCouncilError):
    """Raised when the vector store retrieval step fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class AgentExecutionError(GuardianCouncilError):
    """Raised when an agent node in the LangGraph workflow fails."""

    def __init__(self, message: str, agent_name: str = "unknown"):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}", status_code=502)


class MCPToolError(GuardianCouncilError):
    """Raised when an MCP tool call fails."""

    def __init__(self, message: str, tool_name: str = "unknown"):
        self.tool_name = tool_name
        super().__init__(f"[{tool_name}] {message}", status_code=502)


class ValidationFailureError(GuardianCouncilError):
    """Raised when the Validation Agent rejects a generated plan."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)
