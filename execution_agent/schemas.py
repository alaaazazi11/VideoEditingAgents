from pydantic import BaseModel, Field
from typing import Optional, Any


class ExecutionAgentInput(BaseModel):
    """Input to Execution Agent from Parameter Agents layer"""
    final_params: dict[str, dict[str, Any]] = Field(
        ...,
        description="Collected params per feature from Parameter Agents layer"
    )
    selected_features: list[str] = Field(
        ...,
        description="Features in correct execution order from Planning Agent"
    )
    initial_video_url: str = Field(
        ...,
        description="Original video URL from shared state"
    )


class StepResult(BaseModel):
    """Result of a single execution step"""
    feature: str
    input_video_url: str
    output_video_url: str
    success: bool
    error: Optional[str] = None


class ExecutionAgentOutput(BaseModel):
    """Output from Execution Agent"""
    final_video_url: str
    steps: list[StepResult]
    success: bool
    error: Optional[str] = None