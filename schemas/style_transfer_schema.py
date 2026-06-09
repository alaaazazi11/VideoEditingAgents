from typing import Optional, Literal
from pydantic import Field, model_validator
from schemas.base_schema import BaseSchema

class StyleTransferParams(BaseSchema):
    prompt: str = Field(
        ...,
        description=
        "The editing instruction or style description the user wants to apply to the video (e.g. 'make it look like anime', 'apply oil painting style')"
        "Always interpret indirect phrases (e.g., 'turn it into a 90s cartoon' -> '90s classic cartoon animation style'). "
            "Do not hallucinate facts or parameters not mentioned by the user."
          "Do NOT include any mention of background filling, widening, or expanding the video sides — those belong to the outpainting feature. Only describe the style or visual transformation to apply to the video content itself here.",
         
    )
    video_url: str = Field(
        ...,
        description="The URL of the input video to apply style transfer on. Must be MP4 or MOV format, 2-10 seconds duration, max 100MB",

    )
    reference_image_url: Optional[str] = Field(
        default=None,
        description="Optional URL of a reference image to guide the style transfer visually"
        "When provided, the model will extract colors, textures, and visual composition from this image "
        "to guide the style transfer process." ,
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="1080p",
        description="The output video resolution",
    )

    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4", "input"] = Field(
        default="input",
        description="""The output video aspect ratio. Defaults to the input video's original ratio.
        Automatically map platform names and common phrases to the correct ratio:
        - '9:16' → for 'Reels', 'TikTok', 'Shorts', 'vertical video', 'portrait'
        - '16:9' → for 'YouTube', 'widescreen', 'landscape', 'horizontal video'
        - '1:1' → for 'Instagram post', 'square video'
        - '4:3' → for 'classic TV format'
        - '3:4' → for 'portrait photo format'
        - 'input' → keep the original video ratio (default, use when user doesn't mention anything)
        Example: 'make it for TikTok' → 9:16
        Example: 'I want to post it on YouTube' → 16:9
        Example: 'square format' → 1:1""",
    )


    duration: int = Field(
    default=0,
    ge=0,
    le=10,
    description="""Controls the length of the STYLED OUTPUT video by truncating/shortening it.
    - 0: keep the same length as the input video (default)
    - 2-10: trim the styled output to this many seconds from the start

    ONLY extract this if the user explicitly talks about shortening or trimming the video. Examples:
    - 'trim it to 5 seconds' → duration=5
    - 'I only want 3 seconds of the styled video' → duration=3
    - 'shorten it to 4 seconds' → duration=4

    Do NOT extract this if the user mentions any of these — they belong to a different feature:
    - 'extend', 'add seconds', 'make it longer', 'lengthen', 'add more time'
    
    Note: value must be 0 OR between 2-10. Value of 1 is NOT valid.""",
       )
    
    audio_setting: Literal["auto", "origin"] = Field(
        default="auto",
        description="Controls audio handling. 'auto' lets the model decide, 'origin' preserves the original video audio",
    )


    seed: Optional[int] = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducible output. Use the same seed to get the same result",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Whether to enable content moderation on input and output",
    )

    @model_validator(mode="after")
    def validate_duration(self):
        if self.duration != 0 and self.duration < 2:
            raise ValueError("duration must be 0 (match input) or between 2-10 seconds")
        return self