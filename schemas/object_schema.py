

from typing import Literal, Optional
from pydantic import Field
from schemas.base_schema import BaseSchema

class ObjectParams(BaseSchema):
    video_url: str = Field(
        ...,
        description="The URL of the input video to perform the swap on. Must be a valid URL.",
    )
    image_url: str = Field(
        ...,
        description="The URL of the target image that will be swapped INTO the video. This is what will replace the existing person, object, or background. Example: if you want to replace a person's face with another face, provide the image of that face here. Must be a valid URL.",
    )
    mode: Literal["person", "object", "background"] = Field(
        default="person",
        description="""What type of thing to swap in the video. The model will automatically detect and replace it:
        - person: detects and swaps a person or face in the video with the provided image. Example: 'replace the man's face with the image I provided'
        - object: detects and swaps a specific object in the video with the provided image. Example: 'replace the red car with the image I provided'
        - background: detects and replaces the entire background of the video with the provided image. Example: 'replace the background with a beach scene'""",
    )
    keyframe_id: int = Field(
        default=1,
        ge=1,
        description="""The specific frame number to use as a reference point for detecting the face/object to swap.
        The video is normalized to 24 FPS before processing:
        - keyframe 1 = first frame (start of video)
        - keyframe 24 = 1 second into the video
        - keyframe 48 = 2 seconds into the video
        - Max value = video duration in seconds × 24
        Use this to point the model to a frame where the person/object is most clearly visible for better detection accuracy.
        Example: if the person's face is clearest at 2 seconds, use keyframe_id = 48""",
    )
    resolution: Literal["360p", "540p", "720p"] = Field(
        default="720p",
        description="""The output video resolution. Note: 1080p is NOT supported for this feature.
        - 360p: lowest quality, smallest file size
        - 540p: medium quality
        - 720p: highest available quality (recommended)""",
    )
    original_sound_switch: bool = Field(
        default=True,
        description="""Whether to keep the original audio from the input video in the output.
        - true: preserves the original video audio (recommended)
        - false: removes the original audio from the output""",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible output. If you use the same seed with the same inputs, you get the same result every time. Useful for testing or recreating a specific output. Any integer value works.",
    )