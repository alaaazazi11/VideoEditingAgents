from typing import Literal, Optional
from pydantic import Field, model_validator
from schemas.base_schema import BaseSchema

class OutpaintingParams(BaseSchema):
    prompt: str = Field(
        ...,
        description="Text description of what should appear in the NEW expanded areas beyond the original video frame — this is about the content to generate in the new space, not about any transformation of the existing video. Example: 'more sky and clouds', 'forest extending to the sides', 'city street continuing to the left",
    )
    prompt: str = Field(
    ...,
    description="""Text prompt to guide what should appear in the NEW expanded areas beyond the original video frame.
    This is ONLY about the content to generate in the new expanded space — not about any visual style transformation.
    
    ONLY describe what should fill the new expanded sides/top/bottom. Examples:
    - 'sprawling dense jungle and towering trees' 
    - 'city street continuing to the left' 
    - 'ocean waves extending to the right' 
    - 'more sky and clouds extending above' 
    - 'forest extending to the sides' 
    - 'city street continuing to the left'
    - 'ocean waves extending to the right' 
    - 'sprawling dense jungle and towering trees' 
    - 'cozy aesthetic kitchen background on the sides' 
    
    Do NOT include any of these — they belong to other features:
    - Style descriptions like 'anime style', 'oil painting', 'cinematic' → belongs to style transfer
    - Audio or lip sync instructions → belongs to lip sync feature
    """,
)
    video_url: str = Field(
        ...,
        description="The URL of the source video to outpaint. Must be a valid URL",
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="What to avoid in the generated content (e.g. 'borders, artifacts, low quality')",
    )
    expand_left: bool = Field(
        default=False,
        description="Whether to expand the video to the left side",
    )
    expand_right: bool = Field(
        default=False,
        description="Whether to expand the video to the right side",
    )
    expand_top: bool = Field(
        default=False,
        description="Whether to expand the video to the top",
    )
    expand_bottom: bool = Field(
        default=False,
        description="Whether to expand the video to the bottom",
    )
    expand_ratio: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="How much to expand on each specified side as a fraction of the original size (0.0-1.0)",
    )
    resolution: Literal["auto", "240p", "360p", "480p", "580p", "720p"] = Field(
        default="auto",
        description="The output video resolution",
    )
    aspect_ratio: Literal["auto", "16:9", "1:1", "9:16"] = Field(
        default="auto",
        description="The output video aspect ratio",
    )
    num_frames: int = Field(
        default=81,
        ge=81,
        le=241,
        description="Number of frames in the output video. Must be between 81-241",
    )
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=30,
        description="Frames per second of the output video. Must be between 5-30",
    )
    match_input_num_frames: Optional[bool] = Field(
        default=None,
        description="If True, output frame count matches the input video frame count",
    )
    match_input_frames_per_second: Optional[bool] = Field(
        default=None,
        description="If True, output fps matches the input video fps",
    )
    num_inference_steps: int = Field(
        default=30,
        ge=1,
        description="Number of inference steps. Higher = better quality but slower",
    )
    guidance_scale: float = Field(
        default=5.0,
        ge=0.0,
        description="Guidance strength. Higher values follow the prompt more strictly",
    )
    sampler: Literal["unipc", "dpm++", "euler"] = Field(
        default="unipc",
        description="The sampling algorithm to use for generation",
    )
    shift: float = Field(
        default=5.0,
        description="Shift parameter for video generation",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible output",
    )
    acceleration: Literal["none", "low", "regular"] = Field(
        default="regular",
        description="Generation acceleration level",
    )
    video_quality: Literal["low", "medium", "high", "maximum"] = Field(
        default="high",
        description="The quality of the output video",
    )
    video_write_mode: Literal["fast", "balanced", "small"] = Field(
        default="balanced",
        description="The write mode of the output video",
    )
    interpolator_model: Literal["rife", "film"] = Field(
        default="film",
        description="Frame interpolation method: rife (faster) or film (higher quality)",
    )
    num_interpolated_frames: int = Field(
        default=0,
        ge=0,
        description="Number of frames to interpolate between original frames",
    )
    temporal_downsample_factor: int = Field(
        default=0,
        ge=0,
        description="Number of frames to skip during processing. 0 means no downsampling",
    )
    enable_auto_downsample: Optional[bool] = Field(
        default=None,
        description="If True, automatically detects the optimal temporal downsample factor",
    )
    auto_downsample_min_fps: float = Field(
        default=15.0,
        ge=0.0,
        description="Minimum fps target when auto downsampling is enabled",
    )
    transparency_mode: Literal["content_aware", "white", "black"] = Field(
        default="content_aware",
        description="Fill mode for transparent areas",
    )
    ref_image_urls: Optional[list[str]] = Field(
        default=None,
        description="Optional list of reference image URLs to guide the generation",
    )
    first_frame_url: Optional[str] = Field(
        default=None,
        description="Optional URL of an image to use as the first frame reference",
    )
    last_frame_url: Optional[str] = Field(
        default=None,
        description="Optional URL of an image to use as the last frame reference",
    )
    enable_safety_checker: Optional[bool] = Field(
        default=None,
        description="Whether to enable safety checker on the output",
    )
    enable_prompt_expansion: Optional[bool] = Field(
        default=None,
        description="Whether to automatically expand and enrich the prompt before generation",
    )
    sync_mode: Optional[bool] = Field(
        default=None,
        description="If True, returns media directly as data URI",
    )
    return_frames_zip: Optional[bool] = Field(
        default=None,
        description="If True, also returns a ZIP file containing all generated frames",
    )

    @model_validator(mode="after")
    def validate_expansion_directions(self):
        if not any([
            self.expand_left,
            self.expand_right,
            self.expand_top,
            self.expand_bottom
        ]):
            raise ValueError(
                "At least one expansion direction must be True: "
                "expand_left, expand_right, expand_top, or expand_bottom"
            )
        return self