from execution_agent.runners.base_runner import BaseRunner


class StyleTransferRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="style_transfer",
            endpoint="fal-ai/wan/v2.7/edit-video"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "prompt": params.get("prompt"),
            "video_url": params.get("video_url"),
            "reference_image_url": params.get("reference_image_url"),
            "resolution": params.get("resolution", "1080p"),
            "aspect_ratio": params.get("aspect_ratio"),
            "duration": params.get("duration", 0),
            "audio_setting": params.get("audio_setting", "auto"),
            "seed": params.get("seed"),
            "enable_safety_checker": params.get("enable_safety_checker", True),
        }