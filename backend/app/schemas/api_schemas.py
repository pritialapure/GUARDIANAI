"""
API request/response schemas.

Kept separate from app/schemas/agent_schemas.py (internal LLM structured
outputs) — these are the public contract the frontend depends on.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- /chat ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message.")
    thread_id: str = Field(..., description="Conversation thread ID. Reuse to continue a conversation.")
    location: Optional[str] = Field(None, description="Human-readable location, if known.")
    country: Optional[str] = Field(None, description="Country, used for emergency contact lookup.")


class ChatResponse(BaseModel):
    thread_id: str
    response: str
    requires_emergency_workflow: bool
    emergency_type: Optional[str] = None
    classification_confidence: Optional[float] = None
    action_plan: Optional[Dict[str, Any]] = None
    validation_passed: Optional[bool] = None
    unsupported_claims: List[str] = Field(default_factory=list)
    source_references: List[Dict[str, Any]] = Field(default_factory=list)
    mcp_tool_results: List[Dict[str, Any]] = Field(default_factory=list)
    final_report: Optional[Dict[str, Any]] = None


# --- /ingest ---
class IngestRequest(BaseModel):
    force: bool = Field(False, description="Re-ingest PDFs even if already indexed.")


class IngestResponse(BaseModel):
    newly_ingested_files: List[str]
    skipped_already_indexed: List[str]
    failed_files: List[str]
    total_chunks_added: int


# --- /health ---
class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    google_api_key_configured: bool
    knowledge_base_indexed_documents: int


# --- /agents ---
class AgentInfo(BaseModel):
    name: str
    role: str


class MCPToolInfo(BaseModel):
    name: str
    description: str


class AgentsResponse(BaseModel):
    agents: List[AgentInfo]
    mcp_tools: List[MCPToolInfo]


# --- /documents ---
class DocumentsResponse(BaseModel):
    indexed_files: List[str]
    total_chunks: int
    pending_files: List[str] = Field(
        default_factory=list, description="PDFs present in knowledge_base/ but not yet ingested."
    )


# --- /report ---
class ReportRequest(BaseModel):
    thread_id: str = Field(..., description="Thread ID of a completed emergency workflow run.")


class ReportResponse(BaseModel):
    thread_id: str
    final_report: Dict[str, Any]
