"""
Pydantic schemas for structured agent LLM outputs.

Using `with_structured_output(Schema)` instead of parsing free-text
keeps every agent's output type-safe and directly usable by the next
node in the LangGraph workflow.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class EmergencyType(str, Enum):
    FIRE = "Fire"
    FLOOD = "Flood"
    EARTHQUAKE = "Earthquake"
    MEDICAL = "Medical"
    CHEMICAL_LEAK = "Chemical Leak"
    ELECTRICAL = "Electrical"
    EXPLOSION = "Explosion"
    ROAD_ACCIDENT = "Road Accident"
    VIOLENCE = "Violence"
    OTHER = "Other"


class CoordinatorDecision(BaseModel):
    """Output of the Coordinator Agent: routes the query into the right path."""

    requires_emergency_workflow: bool = Field(
        description="True if the user's message describes or asks about an actual "
        "emergency situation requiring classification, retrieval, and a response "
        "plan. False for greetings, small talk, or completely unrelated questions."
    )
    reasoning: str = Field(description="One or two sentences explaining the routing decision.")


class ClassificationResult(BaseModel):
    """Output of the Emergency Classification Agent."""

    emergency_type: EmergencyType = Field(description="The single best-matching emergency category.")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in this classification, from 0.0 to 1.0."
    )
    reasoning: str = Field(description="Brief justification citing key details from the user's message.")


class ActionStep(BaseModel):
    """A single, ordered step within an emergency action plan."""

    step_number: int
    action: str = Field(description="The concrete action to take.")
    priority: str = Field(description="One of: immediate, urgent, standard.")
    rationale: str = Field(description="Why this step matters, grounded in retrieved context.")


class ActionPlan(BaseModel):
    """Output of the Planning Agent: a structured emergency response plan."""

    emergency_type: str
    summary: str = Field(description="One-paragraph overview of the situation and response strategy.")
    immediate_actions: List[ActionStep] = Field(
        description="Steps that must be taken within the first few minutes."
    )
    follow_up_actions: List[ActionStep] = Field(
        description="Steps to take after the immediate danger is addressed."
    )
    warnings: List[str] = Field(description="Critical safety warnings responders must not ignore.")
    resources_needed: List[str] = Field(description="Personnel, equipment, or agencies to involve.")


class ValidationResult(BaseModel):
    """Output of the Validation Agent: grounding check on the generated plan."""

    passed: bool = Field(description="True only if every recommendation is supported by retrieved context.")
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Any specific recommendations in the plan NOT backed by the retrieved context.",
    )
    notes: List[str] = Field(
        default_factory=list, description="Additional grounding observations or caveats for the reviewer."
    )


class IncidentReport(BaseModel):
    """Output of the Report Generator Agent: the final structured incident report."""

    title: str = Field(description="Short descriptive title for the incident.")
    emergency_type: str
    severity: str = Field(description="One of: low, moderate, high, critical.")
    situation_summary: str = Field(description="Plain-language summary of the reported situation.")
    response_plan_summary: str = Field(description="Condensed summary of the recommended action plan.")
    grounding_status: str = Field(
        description="One of: fully_grounded, partially_grounded, ungrounded — reflects validation outcome."
    )
    responder_message: str = Field(
        description="The final, human-readable message to show the emergency responder, combining the "
        "situation, plan, and any caveats, written clearly and without markdown."
    )
