from typing import Literal

from pydantic import BaseModel, Field


class MaintenanceExtraction(BaseModel):
    """Structured and policy-grounded result produced by Gemini."""

    summary: str = Field(description="A concise maintenance-ticket summary.")
    equipment_type: str | None = Field(
        default=None,
        description="The equipment or asset involved, or null when unknown.",
    )
    issue_category: Literal[
        "mechanical",
        "electrical",
        "plumbing",
        "hvac",
        "safety",
        "structural",
        "other",
    ]
    symptoms: list[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high", "critical"]
    safety_risk: bool
    safety_notes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    policy_citations: list[str] = Field(
        default_factory=list,
        description="Only policy IDs supplied in the prompt may be cited.",
    )
    requires_human_review: bool
    confidence: float = Field(ge=0.0, le=1.0)
