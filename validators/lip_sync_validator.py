from .base_validator import BaseValidator, ValidationError

class LipSyncValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        self.clear_errors()

        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        if "audio_url" in params:
            self.validate_url("audio_url", params["audio_url"])

        if "sync_mode" in params:
            self.validate_enum(
                "sync_mode",
                params["sync_mode"],
                ["cut_off", "loop", "bounce", "silence", "remap"]
            )

        return not self.has_errors(), self.get_errors()