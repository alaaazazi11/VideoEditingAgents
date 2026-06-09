
from typing import Literal, Optional
from pydantic import Field, model_validator
from schemas.base_schema import BaseSchema

class UpscalingParams(BaseSchema):
    video_url: str = Field(
        ...,
        description="The URL of the input video to be upscaled. Must be a valid URL",
    )
    upscale_mode: Literal["target", "factor"] = Field(
        default="factor",
        description="""How to specify the upscaling amount. Choose based on what the user says:
        - factor: use this when the user says something like 'upscale by 2x', 'double the quality', '4x upscale' — uses upscale_factor param
        - target: use this when the user says something like 'upscale to 1080p', 'make it 4K', 'I want 720p output' — uses target_resolution param
        Example: 'upscale the video to 4K' → mode=target, target_resolution=2160p
        Example: 'upscale the video by 2x' → mode=factor, upscale_factor=2.0""",
    )
    upscale_factor: float = Field(
        default=2.0,
        description="""The upscaling multiplier — ONLY used when upscale_mode is 'factor'. 
        Multiplies the original resolution by this number.
        Example: original is 480p, upscale_factor=2.0 → output is 960p
        Example: 'upscale by 4x' → upscale_factor=4.0
        Example: 'double the resolution' → upscale_factor=2.0
        Do NOT extract this if the user specified a target resolution like '1080p' or '4K'""",
    )
    target_resolution: Literal["720p", "1080p", "1440p", "2160p"] = Field(
        default="1080p",
        description="""The specific output resolution to upscale to — ONLY used when upscale_mode is 'target'.
        - 720p: HD quality
        - 1080p: Full HD quality
        - 1440p: 2K quality
        - 2160p: 4K ultra HD quality
        Example: 'upscale to 4K' → target_resolution=2160p
        Example: 'make it 1080p' → target_resolution=1080p
        Example: 'I want Full HD' → target_resolution=1080p
        Do NOT extract this if the user said something like '2x' or 'double the resolution'""",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible output. Use the same seed with the same inputs to get the same result every time. Any integer value works.",
    )
    noise_scale: float = Field(
        default=0.1,
        description="""Controls how much detail/texture enhancement is added during upscaling. 
        Higher values add more sharpness and detail but may introduce noise.
        Lower values produce smoother but less detailed output.
        Example: 'make it sharper' → increase noise_scale
        Example: 'keep it smooth' → decrease noise_scale
        Range: 0.0 (no enhancement) to 1.0 (maximum enhancement)""",
    )
    output_format: Literal["X264 (.mp4)", "VP9 (.webm)", "PRORES4444 (.mov)", "GIF (.gif)"] = Field(
        default="X264 (.mp4)",
        description="""The output video file format:
        - X264 (.mp4): most compatible format, works everywhere (recommended, default)
        - VP9 (.webm): web-optimized format, smaller file size
        - PRORES4444 (.mov): professional high quality format for video editing
        - GIF (.gif): animated gif format, no audio
        Example: 'I want an mp4' → X264 (.mp4)
        Example: 'export as webm' → VP9 (.webm)
        Example: 'I need it for video editing' → PRORES4444 (.mov)""",
    )
    output_quality: Literal["low", "medium", "high", "maximum"] = Field(
        default="high",
        description="""The quality level of the output video. Higher quality means better looking video but larger file size and slower processing:
        - low: smallest file, fastest, lowest quality
        - medium: balanced quality and size
        - high: good quality, recommended for most use cases (default)
        - maximum: best possible quality, largest file size, slowest
        Example: 'I want the best quality' → maximum
        Example: 'keep the file small' → low or medium""",
    )
    output_write_mode: Literal["fast", "balanced", "small"] = Field(
        default="balanced",
        description="""Controls the trade-off between processing speed and output file size:
        - fast: processes faster but produces larger files
        - balanced: good balance between speed and file size (default)
        - small: produces smallest file size but takes longer to process
        Example: 'I need it quickly' → fast
        Example: 'I need a small file' → small""",
    )
    sync_mode: bool = Field(
        default=False,
        description="""Controls how the output is returned:
        - false: saves the output video and returns a download URL (default, recommended)
        - true: returns the video directly as data — output is NOT saved in history
        Most users should keep this as false unless they specifically need inline data output.""",
    )

    @model_validator(mode="after")
    def validate_upscale_mode_params(self):
        if self.upscale_mode == "factor" and self.upscale_factor is None:
            raise ValueError("upscale_factor is required when upscale_mode is 'factor'")
        if self.upscale_mode == "target" and self.target_resolution is None:
            raise ValueError("target_resolution is required when upscale_mode is 'target'")
        return self