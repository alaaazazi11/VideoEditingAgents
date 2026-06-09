from .base_validator import BaseValidator, ValidationError


class UpscalingValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all upscaling params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate upscale_mode
        if "upscale_mode" in params:
            self.validate_enum(
                "upscale_mode",
                params["upscale_mode"],
                ["target", "factor"]
            )

        # validate upscale_factor vs target_resolution based on upscale_mode
        upscale_mode = params.get("upscale_mode", "factor")

        if upscale_mode == "factor":
            if "upscale_factor" in params:
                self.validate_float_range(
                    "upscale_factor",
                    params["upscale_factor"],
                    0.1,
                    16.0
                )
        elif upscale_mode == "target":
            if "target_resolution" in params:
                self.validate_enum(
                    "target_resolution",
                    params["target_resolution"],
                    ["720p", "1080p", "1440p", "2160p"]
                )

        # validate noise_scale
        if "noise_scale" in params:
            self.validate_float_range(
                "noise_scale",
                params["noise_scale"],
                0.0,
                1.0
            )

        # validate output_format
        if "output_format" in params:
            self.validate_enum(
                "output_format",
                params["output_format"],
                ["X264 (.mp4)", "VP9 (.webm)", "PRORES4444 (.mov)", "GIF (.gif)"]
            )

        # validate output_quality
        if "output_quality" in params:
            self.validate_enum(
                "output_quality",
                params["output_quality"],
                ["low", "medium", "high", "maximum"]
            )

        # validate output_write_mode
        if "output_write_mode" in params:
            self.validate_enum(
                "output_write_mode",
                params["output_write_mode"],
                ["fast", "balanced", "small"]
            )

        # validate sync_mode
        if "sync_mode" in params:
            self.validate_boolean("sync_mode", params["sync_mode"])

        # validate seed
        if params.get("seed") is not None:
            self.validate_integer_range("seed", params["seed"], 0, 2147483647)

        return not self.has_errors(), self.get_errors()