from execution_agent.runners.base_runner import BaseRunner


class KlingRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="kling",
            endpoint="fal-ai/kling-video/o3/pro/video-to-video/edit"  # ✅ fixed
        )

    def build_input(self, params: dict) -> dict:
        # Serialize elements if they're Pydantic objects
        elements = params.get("elements")
        if elements:
            elements = [e if isinstance(e, dict) else e.dict() for e in elements]

        return {
            "prompt": params.get("prompt"),
            "video_url": params.get("video_url"),
            "image_urls": params.get("image_urls"),
            "keep_audio": params.get("keep_audio", True),
            "elements": elements,
            "shot_type": params.get("shot_type", "customize"),
        }
