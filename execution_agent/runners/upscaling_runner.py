from execution_agent.runners.base_runner import BaseRunner


class UpscalingRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="upscaling",
            endpoint="fal-ai/seedvr/upscale/video"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "video_url": params.get("video_url"),
            "upscale_mode": params.get("upscale_mode", "factor"),
            "upscale_factor": params.get("upscale_factor", 2.0),
            "target_resolution": params.get("target_resolution", "1080p"),
            "seed": params.get("seed"),
            "noise_scale": params.get("noise_scale", 0.1),
            "output_format": params.get("output_format", "X264 (.mp4)"),
            "output_quality": params.get("output_quality", "high"),
            "output_write_mode": params.get("output_write_mode", "balanced"),
            "sync_mode": params.get("sync_mode", False),
        }