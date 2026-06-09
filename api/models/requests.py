from pydantic import BaseModel, Field
from typing import Optional

class StartChatRequest(BaseModel):
    user_prompt: str
    video_placeholder: str = "@Video1"
    image_placeholders: list[str] = []
    audio_placeholder: Optional[str] = None
    uploaded_files: dict[str, str] = Field(
        ...,
        description="Dict of placeholder → URL from upload endpoints e.g. {'@Video1': 'https://...'}"
    )



class ContinueChatRequest(BaseModel):
    """
    Follow-up message from user in an existing session.
    Used for:
    - Answering agent questions about missing params
    - Confirming or rejecting the plan
    - Requesting plan changes
    """
    session_id: str = Field(
        ...,
        description="The session ID from StartChatResponse"
    )
    message: str = Field(
        ...,
        description="The user's reply"
    )


class ConfirmPlanRequest(BaseModel):
    """
    User confirms or rejects the plan.
    """
    session_id: str
    confirmed: bool = Field(
        ...,
        description="True = confirmed, False = request changes"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Feedback message when confirmed=False"
    )