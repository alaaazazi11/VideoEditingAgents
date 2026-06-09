from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────
# Input
# ─────────────────────────────────────────

class RoutingAgentInput(BaseModel):
    """Input to Routing Agent from FastAPI"""
    user_prompt: str = Field(..., description="Original user prompt")
    video_metadata: dict = Field(..., description="Video metadata including duration, width, height")
    file_references: dict = Field(
        default={},
        description="Uploaded file placeholders mapped to URLs e.g. {'@Video1': 'url', '@Image1': 'url'}"
    )
    user_feedback: Optional[str] = Field(
        default=None,
        description="User feedback when requesting plan changes — only present when replanning"
    )
    previous_plan: Optional[dict] = Field(
        default=None,
        description="Previous plan — only present when replanning"
    )


# ─────────────────────────────────────────
# Atomic Edit
# ─────────────────────────────────────────

class AtomicEdit(BaseModel):
    """Single atomic edit extracted from user prompt"""
    edit_description: str = Field(
        ...,
        description="Plain English description of this single edit"
    )
    matched_feature: str = Field(
        ...,
        description="The feature that handles this edit e.g. 'style_transfer', 'outpainting'"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How confident the agent is about this feature match (0.0 - 1.0)"
    )


# ─────────────────────────────────────────
# Output
# ─────────────────────────────────────────

class RoutingAgentOutput(BaseModel):
    """Output from Routing Agent to Planning Agent"""
    user_prompt: str
    atomic_edits: list[AtomicEdit] = Field(
        ...,
        description="List of atomic edits extracted from user prompt"
    )
    selected_features: list[str] = Field(
        ...,
        description="List of selected feature names e.g. ['style_transfer', 'outpainting']"
    )
    tier: str = Field(
        ...,
        description="basic or advanced"
    )
    tier_reasoning: str = Field(
        ...,
        description="Plain English explanation of why this tier was chosen"
    )
    basic_total_cost: float = Field(
        ...,
        description="Total cost if using Basic tier"
    )
    kling_total_cost: float = Field(
        ...,
        description="Total cost if using Advanced tier (Kling)"
    )
    video_metadata: dict
    file_references: dict