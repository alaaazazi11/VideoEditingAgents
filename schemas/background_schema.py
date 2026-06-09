from typing import Literal, Optional
from pydantic import Field, model_validator
from schemas.base_schema import BaseSchema

class BackgroundParams(BaseSchema):
    video_url: str = Field(
        ...,
        description="The URL of the input video to remove  background from. Must be a valid URL",
    )
    model: Literal[
        "General Use (Light)",
        "General Use (Light 2K)",
        "General Use (Heavy)",
        "Matting",
        "Portrait",
        "General Use (Dynamic)"
    ] = Field(
        default="General Use (Light)",
        description="""The model to use for background removal:
        - General Use (Light): fastest, recommended for most use cases
        - General Use (Light 2K): same as Light but trained with 2K images
        - General Use (Heavy): slower but more accurate
        - Matting: specifically trained for matting
        - Portrait: specifically trained for portrait videos
        - General Use (Dynamic): supports dynamic resolutions from 256x256 to 2304x2304""",
    )
    operating_resolution: Literal["1024x1024", "2048x2048", "2304x2304"] = Field(
        default="1024x1024",
        description="""The resolution to operate on:
        - 1024x1024: default, works with all models
        - 2048x2048: higher accuracy for high res input
        - 2304x2304: only available with 'General Use (Dynamic)' model""",
    )
    output_mask: Optional[bool] = Field(
        default=None,
        description="Whether to output the mask used to remove the background alongside the video",
    )
    refine_foreground: bool = Field(
        default=True,
        description="Whether to refine the foreground edges using the estimated mask for cleaner output",
    )
    sync_mode: Optional[bool] = Field(
        default=None,
        description="If True, returns media directly as data URI instead of saving to history",
    )
    video_output_type: Literal["X264 (.mp4)", "VP9 (.webm)", "PRORES4444 (.mov)", "GIF (.gif)"] = Field(
        default="X264 (.mp4)",
        description="The output video format",
    )
    video_quality: Literal["low", "medium", "high", "maximum"] = Field(
        default="high",
        description="The quality of the output video",
    )
    video_write_mode: Literal["fast", "balanced", "small"] = Field(
        default="balanced",
        description="""The write mode of the output video:
        - fast: faster processing, larger file
        - balanced: balance between speed and size
        - small: slower processing, smaller file""",
    )

    @model_validator(mode="after")
    def validate_operating_resolution(self):
        if self.operating_resolution == "2304x2304" and self.model != "General Use (Dynamic)":
            raise ValueError(
                "operating_resolution '2304x2304' is only available with 'General Use (Dynamic)' model."
            )
        return self