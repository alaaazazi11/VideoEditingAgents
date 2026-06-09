from .base_validator import BaseValidator, ValidationError


class StyleTransferValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all style transfer params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_video_url("video_url", params["video_url"])

        # validate reference_image_url if provided
        if params.get("reference_image_url"):
            self.validate_url("reference_image_url", params["reference_image_url"])

        # validate resolution
        if "resolution" in params:
            self.validate_enum(
                "resolution",
                params["resolution"],
                ["720p", "1080p"]
            )

        # validate aspect_ratio
        if "aspect_ratio" in params:
            self.validate_enum(
                "aspect_ratio",
                params["aspect_ratio"],
                ["16:9", "9:16", "1:1", "4:3", "3:4", "input"]
            )

        # validate duration
        if "duration" in params:
            duration = params["duration"]
            if duration != 0 and not (2 <= duration <= 10):
                self.errors.append(ValidationError(
                    param="duration",
                    reason="duration must be 0 (match input) or between 2-10 seconds",
                    valid_options=[0, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                ))

        # validate audio_setting
        if "audio_setting" in params:
            self.validate_enum(
                "audio_setting",
                params["audio_setting"],
                ["auto", "origin"]
            )

        # validate seed
        if params.get("seed") is not None:
            self.validate_integer_range("seed", params["seed"], 0, 2147483647)

        # validate enable_safety_checker
        if "enable_safety_checker" in params:
            self.validate_boolean("enable_safety_checker", params["enable_safety_checker"])

        # validate prompt
        if "prompt" in params:
            self.validate_string("prompt", params["prompt"])

        return not self.has_errors(), self.get_errors()