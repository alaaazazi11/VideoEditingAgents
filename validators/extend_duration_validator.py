from .base_validator import BaseValidator, ValidationError


class ExtendDurationValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all extend duration params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate prompt
        if "prompt" in params:
            self.validate_string("prompt", params["prompt"])

        # validate duration
        if "duration" in params:
            self.validate_float_range(
                "duration",
                params["duration"],
                5.0,
                20.0
            )

        # validate mode
        if "mode" in params:
            self.validate_enum(
                "mode",
                params["mode"],
                ["start", "end"]
            )

        # validate context using shared state video duration
        if params.get("context") is not None:
            self.validate_context("context", params["context"])

        # validate resolution
        if "resolution" in params:
            self.validate_enum(
                "resolution",
                params["resolution"],
                ["1080p", "1440p", "2160p"]
            )

        # validate aspect_ratio
        if "aspect_ratio" in params:
            self.validate_enum(
                "aspect_ratio",
                params["aspect_ratio"],
                ["auto", "16:9", "9:16"]
            )

        # validate fps
        if "fps" in params:
            self.validate_enum(
                "fps",
                params["fps"],
                [24, 25, 48, 50]
            )

        # validate generate_audio
        if "generate_audio" in params:
            self.validate_boolean("generate_audio", params["generate_audio"])

        # validate auto_fix
        if "auto_fix" in params:
            self.validate_boolean("auto_fix", params["auto_fix"])

        # validate safety_tolerance
        if "safety_tolerance" in params:
            self.validate_integer_range(
                "safety_tolerance",
                params["safety_tolerance"],
                1,
                6
            )

        # validate seed
        if params.get("seed") is not None:
            self.validate_integer_range("seed", params["seed"], 0, 2147483647)

        return not self.has_errors(), self.get_errors()