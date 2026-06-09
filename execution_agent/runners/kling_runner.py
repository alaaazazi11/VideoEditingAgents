from execution_agent.runners.base_runner import BaseRunner





class KlingRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="kling",
            endpoint="fal-ai/kling-video/o1/video-to-video/edit"  # ← correct endpoint
        )

    def build_input(self, params: dict) -> dict:
        return {
            "prompt": params.get("prompt"),
            "video_url": params.get("video_url"),
            "image_urls": params.get("image_urls"),
            "keep_audio": params.get("keep_audio", True),
            "elements": [
                {
                    "reference_image_urls": e.get("reference_image_urls", []),
                    "frontal_image_url": e.get("frontal_image_url")
                }
                for e in params.get("elements", [])
            ] if params.get("elements") else None,
        }