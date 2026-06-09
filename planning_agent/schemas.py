from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────
# Input
# ─────────────────────────────────────────

class PlanningAgentInput(BaseModel):
    """Input to Planning Agent from Routing Agent"""
    user_prompt: str = Field(..., description="Original user prompt")
    selected_features: list[str] = Field(..., description="Features selected by Routing Agent")
    tier: str = Field(..., description="basic or advanced")
    video_metadata: dict = Field(..., description="Video metadata including duration, width, height")
    user_feedback: Optional[str] = Field(
        default=None,
        description="User feedback from previous plan — only present when replanning"
    )
    previous_plan: Optional[dict] = Field(
        default=None,
        description="Previous plan shown to user — only present when replanning"
    )


# ─────────────────────────────────────────
# Output
# ─────────────────────────────────────────

class PlanStep(BaseModel):
    """Single step in the execution plan"""
    step_number: int
    feature: str
    display_name: str
    cost: float
    cost_details: str
    description: str


class Plan(BaseModel):
    """Full execution plan shown to user"""
    tier: str                          # basic or advanced
    steps: list[PlanStep]              # ordered execution steps
    total_cost: float                  # total cost of all steps
    summary: str                       # human readable summary of what will happen
    selected_features: list[str]       # ordered features for parameter agents


class PlanningAgentOutput(BaseModel):
    """Output from Planning Agent"""
    plan: Plan
    status: str = Field(
        default="awaiting_confirmation",
        description="awaiting_confirmation | confirmed | changes_requested"
    )


# ─────────────────────────────────────────
# User feedback
# ─────────────────────────────────────────

class UserPlanFeedback(BaseModel):
    """User feedback on the plan"""
    session_id: str
    feedback_type: str = Field(
        ...,
        description="confirmed | changes_requested"
    )
    feedback_message: Optional[str] = Field(
        default=None,
        description="User's message when requesting changes"
    )