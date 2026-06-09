from typing import Literal, Optional
from pydantic import Field, model_validator
from schemas.base_schema import BaseSchema

class ExtendDurationParams(BaseSchema):
    video_url: str = Field(
        ...,
        description="The URL of the input video to extend. Must be a valid URL",
    )

    prompt: str = Field(
        ...,
        description="""Text description of what should happen in the NEW extended part of the video.
        This describes the CONTINUATION or NEW CONTENT to generate — not the style of the original video.
        
        ONLY extract this if the user describes what should appear in the extended section. Examples:
        - 'the person continues walking forward' → prompt='the person continues walking forward'
        - 'add more ocean waves at the end' → prompt='ocean waves continuing'
        - 'extend with the car driving away' → prompt='car driving away into the distance'
        
        Do NOT use style descriptions here like 'make it anime' or 'cinematic style' — those belong to style transfer feature.
        Do NOT hallucinate or assume content the user didn't describe.""",
    )

    duration: float = Field(
    default=5.0,
    ge=5.0,
    le=20.0,
    description="""How many seconds to ADD/APPEND to the video. This is about making the video LONGER, not about the total output length.
    Must be between 5-20 seconds.

    ONLY extract this if the user explicitly talks about extending or adding to the video. Examples:
    - 'extend it by 8 seconds' → duration=8
    - 'add 10 more seconds' → duration=10
    - 'make it longer by 6 seconds' → duration=6

    Do NOT extract this if the user mentions any of these — they belong to a different feature:
    - 'trim', 'shorten', 'cut to X seconds', 'I only want X seconds'
    
    Note: must be between 5.0 and 20.0 seconds.""",
)


    mode: Literal["start", "end"] = Field(
        default="end",
        description="""Where to extend the video:
        - end: generates new frames AFTER the last frame (default, most common)
        - start: generates new frames BEFORE the first frame
        
        Example: 'add more content at the end' → end
        Example: 'add an intro before the video' → start
        If user doesn't specify, use default 'end'""",
    )    
    context: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=20.0,
        description="How many seconds of the original video to use as reference context for generation. Must be between 1-20 seconds",
    )
    resolution: Literal["1080p", "1440p", "2160p"] = Field(
        default="1080p",
        description="""The output video resolution:
        - 1080p: Full HD (default, recommended)
        - 1440p: 2K quality
        - 2160p: 4K ultra HD quality
        
        Example: 'I want 4K output' → 2160p
        Example: 'make it 2K' → 1440p""",
    )
    aspect_ratio: Literal["auto", "16:9", "9:16"] = Field(
        default="auto",
        description="""The output video aspect ratio:
        - auto: matches the input video ratio (default)
        - 16:9: widescreen, landscape — for YouTube, TV
        - 9:16: vertical, portrait — for TikTok, Reels, Shorts
        
        Example: 'make it vertical' → 9:16
        Example: 'keep the same ratio' → auto
        If user doesn't mention ratio, use default 'auto'""",
    )
    fps: Literal[24, 25, 48, 50] = Field(
        default=25,
        description="Frames per second of the output video",
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the extended part of the video",
    )

    generate_audio: bool = Field(
    default=True,
    description="""Whether to generate NEW audio for the NEWLY ADDED seconds of the video extension.
    This has NOTHING to do with the original video's audio — it only affects the brand new extended part.
    
    - true: generates new audio for the added seconds (default)
    - false: no audio in the newly added seconds only
    

    Only extract if user explicitly says something like:
    - 'no audio in the extended part' → false
    - 'generate sound for the extension' → true
    If user doesn't mention audio for the extension specifically, use default true""",
     )    
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible output",
    )
    auto_fix: bool = Field(
        default=False,
        description="Whether to automatically correct invalid or problematic prompts before generation",
    )
    safety_tolerance: int = Field(
        default=4,
        ge=1,
        le=6,
        description="""Content safety strictness level:
        - 1: most strict
        - 6: most lenient""",
    )