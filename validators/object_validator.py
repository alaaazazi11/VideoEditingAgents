from .base_validator import BaseValidator, ValidationError


class ObjectValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all object add/replace/remove params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate image_url
        if "image_url" in params:
            self.validate_url("image_url", params["image_url"])

        # validate mode
        if "mode" in params:
            self.validate_enum(
                "mode",
                params["mode"],
                ["person", "object", "background"]
            )

        # validate keyframe_id using shared state video duration
        if "keyframe_id" in params:
            self.validate_keyframe_id("keyframe_id", params["keyframe_id"])

        # validate resolution — note 1080p is NOT supported
        if "resolution" in params:
            self.validate_enum(
                "resolution",
                params["resolution"],
                ["360p", "540p", "720p"]
            )

        # validate original_sound_switch
        if "original_sound_switch" in params:
            self.validate_boolean(
                "original_sound_switch",
                params["original_sound_switch"]
            )

        # validate seed
        if params.get("seed") is not None:
            self.validate_integer_range("seed", params["seed"], 0, 2147483647)

        return not self.has_errors(), self.get_errors()