from execution_agent.runners.base_runner import BaseRunner


class BackgroundRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="background",
            endpoint="fal-ai/birefnet/v2/video"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "video_url": params.get("video_url"),
            "model": params.get("model", "General Use (Light)"),
            "operating_resolution": params.get("operating_resolution", "1024x1024"),
            "output_mask": params.get("output_mask"),
            "refine_foreground": params.get("refine_foreground", True),
            "sync_mode": params.get("sync_mode"),
            "video_output_type": params.get("video_output_type", "X264 (.mp4)"),
            "video_quality": params.get("video_quality", "high"),
            "video_write_mode": params.get("video_write_mode", "balanced"),
        }