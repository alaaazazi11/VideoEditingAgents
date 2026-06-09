from execution_agent.runners.base_runner import BaseRunner


class ExtendDurationRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="extend_duration",
            endpoint="fal-ai/ltx-2.3/extend-video"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "video_url": params.get("video_url"),
            "prompt": params.get("prompt"),
            "duration": params.get("duration", 5.0),
            "mode": params.get("mode", "end"),
            "context": params.get("context"),
        }