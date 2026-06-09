
from typing import Literal
from pydantic import Field
from schemas.base_schema import BaseSchema

class LipSyncParams(BaseSchema):
    video_url: str = Field(
        ...,
        description="The URL of the input video to apply lip sync on. This is the video whose lip movements will be modified to match the provided audio. Must be a valid URL.",
    )
    audio_url: str = Field(
        ...,
        description="""The URL of the audio file that the lip movements will be synced to. 
        The character's lips in the video will move to match this audio track.
        Must be a valid URL pointing to an audio file.
        Example: 'sync the video with this audio https://example.com/speech.mp3' → audio_url=https://example.com/speech.mp3""",
    )
    sync_mode: Literal["cut_off", "loop", "bounce", "silence", "remap"] = Field(
        default="cut_off",
        description="""Controls what happens when the audio and video have different durations. Choose based on what the user wants:
        - cut_off: trims whichever is longer so both end at the same time. Example: 'just cut it off when done' → cut_off
        - loop: loops the shorter one repeatedly until it matches the longer one. Example: 'keep repeating the audio until the video ends' → loop
        - bounce: loops back and forth (forward then reverse) to match duration. Example: 'loop it back and forth' → bounce  
        - silence: if audio is shorter than video, pads the remaining video with silence. Example: 'add silence after the audio ends' → silence
        - remap: stretches or compresses the audio/video to match each other's duration. Example: 'stretch it to fit' or 'compress to match' → remap
        If the user doesn't mention anything about duration mismatch, use the default 'cut_off'""",
    )    