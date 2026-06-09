from execution_agent.runners.base_runner import BaseRunner


class ObjectRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="object",
            endpoint="fal-ai/pixverse/swap"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "video_url": params.get("video_url"),
            "image_url": params.get("image_url"),
            "mode": params.get("mode", "person"),
            "keyframe_id": params.get("keyframe_id", 1),
            "resolution": params.get("resolution", "720p"),
            "original_sound_switch": params.get("original_sound_switch", True),
            "seed": params.get("seed"),
        }