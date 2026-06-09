from typing import TypedDict, Optional, Any
from enum import Enum

class AgentStatus(str, Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    DONE = "done"
    FAILED = "failed"

class VideoMetadata(TypedDict):
    url: str
    format: str
    duration: float
    size_mb: float
    width: int
    height: int

class AgentState(TypedDict):
    status: AgentStatus
    collected_params: dict[str, Any]
    missing_params: list[str]
    invalid_params: list[dict]

class SharedState(TypedDict):
    # Input
    user_prompt: str
    video_metadata: VideoMetadata
    file_references: dict[str, str]

    # Routing Agent output
    selected_features: list[str]
    tier: str                          # basic | advanced
    tier_reasoning: str
    basic_total_cost: float
    kling_total_cost: float

    # Planning Agent output
    plan: Optional[dict]               # full plan dict
    plan_status: str                   # awaiting_confirmation | confirmed | changes_requested
    user_plan_feedback: Optional[str]  # user feedback on plan
   
    # Feature agents state
    agents_state: dict[str, AgentState]

    # Conversation
    conversation_history: list[dict]
    latest_user_reply: Optional[str]
    latest_assistant_message: str

    # Output
    final_params: dict[str, Any]


    skip_planning: bool

    # Execution Agent output
    execution_status: str          # pending | running | done | failed
    execution_output_url: str      # final video URL
    execution_error: Optional[str] # error message if failed
    execution_steps: list[dict]    # step results for logging