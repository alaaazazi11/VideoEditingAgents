from pydantic import BaseModel, Field
from typing import Optional, Any


class UploadResponse(BaseModel):
    """Response after uploading a file"""
    placeholder: str        # e.g. "@Video1", "@Image1", "@Audio1"
    url: str                # fal.ai storage URL
    format: str             # mp4, mov, jpg, wav, etc.
    size_mb: float          # file size in MB


class StartChatResponse(BaseModel):
    """
    Response to first message.
    Creates a new session and returns first agent message.
    """
    session_id: str
    status: str = Field(
        ...,
        description="collecting | awaiting_plan_confirmation | executing | done | failed"
    )
    message: Optional[str] = Field(
        default=None,
        description="Agent message to show user in chat"
    )
    plan: Optional[dict] = Field(
        default=None,
        description="Plan details when status=awaiting_plan_confirmation"
    )


class ContinueChatResponse(BaseModel):
    """
    Response to follow-up message.
    Returns next agent message or final result.
    """
    session_id: str
    status: str = Field(
        ...,
        description="collecting | awaiting_plan_confirmation | executing | done | failed"
    )
    message: Optional[str] = Field(
        default=None,
        description="Agent message to show user in chat"
    )
    plan: Optional[dict] = Field(
        default=None,
        description="Plan details when status=awaiting_plan_confirmation"
    )
    final_video_url: Optional[str] = Field(
        default=None,
        description="Final video URL when status=done"
    )
    execution_steps: Optional[list[dict]] = Field(
        default=None,
        description="Execution steps details when status=done or failed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message when status=failed"
    )


class ConfirmPlanResponse(BaseModel):
    """
    Response after user confirms or rejects plan.
    """
    session_id: str
    status: str = Field(
        ...,
        description="collecting | executing | done | failed"
    )
    message: Optional[str] = Field(
        default=None,
        description="Agent message after confirmation"
    )
    final_video_url: Optional[str] = Field(
        default=None,
        description="Final video URL when status=done"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message when status=failed"
    )


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None