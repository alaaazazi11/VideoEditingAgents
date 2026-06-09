from .base_validator import BaseValidator, ValidationError


class BackgroundValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all background remove/change params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate model
        if "model" in params:
            self.validate_enum(
                "model",
                params["model"],
                [
                    "General Use (Light)",
                    "General Use (Light 2K)",
                    "General Use (Heavy)",
                    "Matting",
                    "Portrait",
                    "General Use (Dynamic)"
                ]
            )

        # validate operating_resolution
        if "operating_resolution" in params:
            self.validate_enum(
                "operating_resolution",
                params["operating_resolution"],
                ["1024x1024", "2048x2048", "2304x2304"]
            )

        # cross-param validation: 2304x2304 only with General Use (Dynamic)
        model = params.get("model", "General Use (Light)")
        operating_resolution = params.get("operating_resolution", "1024x1024")

        if operating_resolution == "2304x2304" and model != "General Use (Dynamic)":
            self.errors.append(ValidationError(
                param="operating_resolution",
                reason=(
                    "'2304x2304' resolution is only available with 'General Use (Dynamic)' model. "
                    f"You selected '{model}'. Please either change operating_resolution or switch model to 'General Use (Dynamic)'"
                ),
                valid_options=["1024x1024", "2048x2048"]
            ))

        # validate output_mask
        if params.get("output_mask") is not None:
            self.validate_boolean("output_mask", params["output_mask"])

        # validate refine_foreground
        if "refine_foreground" in params:
            self.validate_boolean("refine_foreground", params["refine_foreground"])

        # validate sync_mode
        if params.get("sync_mode") is not None:
            self.validate_boolean("sync_mode", params["sync_mode"])

        # validate video_output_type
        if "video_output_type" in params:
            self.validate_enum(
                "video_output_type",
                params["video_output_type"],
                ["X264 (.mp4)", "VP9 (.webm)", "PRORES4444 (.mov)", "GIF (.gif)"]
            )

        # validate video_quality
        if "video_quality" in params:
            self.validate_enum(
                "video_quality",
                params["video_quality"],
                ["low", "medium", "high", "maximum"]
            )

        # validate video_write_mode
        if "video_write_mode" in params:
            self.validate_enum(
                "video_write_mode",
                params["video_write_mode"],
                ["fast", "balanced", "small"]
            )

        return not self.has_errors(), self.get_errors()