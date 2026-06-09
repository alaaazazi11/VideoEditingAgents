from execution_agent.runners.base_runner import BaseRunner


class LipSyncRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="lip_sync",
            endpoint="fal-ai/sync-lipsync/v3"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "video_url": params.get("video_url"),
            "audio_url": params.get("audio_url"),
            "sync_mode": params.get("sync_mode", "cut_off"),
        }