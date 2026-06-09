from .base_validator import BaseValidator, ValidationError


class OutpaintingValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        """
        Validate all outpainting params.
        Returns (is_valid, list of errors)
        """
        self.clear_errors()

        # validate prompt
        if "prompt" in params:
            self.validate_string("prompt", params["prompt"])

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate negative_prompt if provided
        if params.get("negative_prompt") is not None:
            self.validate_string("negative_prompt", params["negative_prompt"])

        # validate expansion directions — at least one must be True
        expand_keys = ["expand_left", "expand_right", "expand_top", "expand_bottom"]
        expand_values = {k: params.get(k, False) for k in expand_keys}

        if not any(expand_values.values()):
            self.errors.append(ValidationError(
                param="expand_left/expand_right/expand_top/expand_bottom",
                reason="At least one expansion direction must be True",
                valid_options=expand_keys
            ))

        # validate each expansion direction boolean
        for key in expand_keys:
            if key in params:
                self.validate_boolean(key, params[key])

        # validate expand_ratio
        if "expand_ratio" in params:
            self.validate_float_range(
                "expand_ratio",
                params["expand_ratio"],
                0.0,
                1.0
            )

        # validate resolution
        if "resolution" in params:
            self.validate_enum(
                "resolution",
                params["resolution"],
                ["auto", "240p", "360p", "480p", "580p", "720p"]
            )

        # validate aspect_ratio
        if "aspect_ratio" in params:
            self.validate_enum(
                "aspect_ratio",
                params["aspect_ratio"],
                ["auto", "16:9", "1:1", "9:16"]
            )

        # validate num_frames
        if "num_frames" in params:
            self.validate_integer_range(
                "num_frames",
                params["num_frames"],
                81,
                241
            )

        # validate frames_per_second
        if "frames_per_second" in params:
            if not params.get("match_input_frames_per_second"):
                self.validate_integer_range(
                    "frames_per_second",
                    params["frames_per_second"],
                    5,
                    30
                )

        # validate match_input_num_frames
        if params.get("match_input_num_frames") is not None:
            self.validate_boolean(
                "match_input_num_frames",
                params["match_input_num_frames"]
            )

        # validate match_input_frames_per_second
        if params.get("match_input_frames_per_second") is not None:
            self.validate_boolean(
                "match_input_frames_per_second",
                params["match_input_frames_per_second"]
            )

        # validate num_inference_steps
        if "num_inference_steps" in params:
            self.validate_integer_range(
                "num_inference_steps",
                params["num_inference_steps"],
                1,
                1000
            )

        # validate guidance_scale
        if "guidance_scale" in params:
            self.validate_float_range(
                "guidance_scale",
                params["guidance_scale"],
                0.0,
                20.0
            )

        # validate sampler
        if "sampler" in params:
            self.validate_enum(
                "sampler",
                params["sampler"],
                ["unipc", "dpm++", "euler"]
            )

        # validate acceleration
        if "acceleration" in params:
            self.validate_enum(
                "acceleration",
                params["acceleration"],
                ["none", "low", "regular"]
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

        # validate interpolator_model
        if "interpolator_model" in params:
            self.validate_enum(
                "interpolator_model",
                params["interpolator_model"],
                ["rife", "film"]
            )

        # validate num_interpolated_frames
        if "num_interpolated_frames" in params:
            self.validate_integer_range(
                "num_interpolated_frames",
                params["num_interpolated_frames"],
                0,
                100
            )

        # validate temporal_downsample_factor
        if "temporal_downsample_factor" in params:
            self.validate_integer_range(
                "temporal_downsample_factor",
                params["temporal_downsample_factor"],
                0,
                100
            )

        # validate enable_auto_downsample
        if params.get("enable_auto_downsample") is not None:
            self.validate_boolean(
                "enable_auto_downsample",
                params["enable_auto_downsample"]
            )

        # validate auto_downsample_min_fps
        if "auto_downsample_min_fps" in params:
            self.validate_float_range(
                "auto_downsample_min_fps",
                params["auto_downsample_min_fps"],
                0.0,
                120.0
            )

        # validate transparency_mode
        if "transparency_mode" in params:
            self.validate_enum(
                "transparency_mode",
                params["transparency_mode"],
                ["content_aware", "white", "black"]
            )

        # validate ref_image_urls if provided
        if params.get("ref_image_urls") is not None:
            if not isinstance(params["ref_image_urls"], list):
                self.errors.append(ValidationError(
                    param="ref_image_urls",
                    reason="ref_image_urls must be a list of URLs",
                ))
            else:
                for i, url in enumerate(params["ref_image_urls"]):
                    self.validate_url(f"ref_image_urls[{i}]", url)

        # validate first_frame_url if provided
        if params.get("first_frame_url") is not None:
            self.validate_url("first_frame_url", params["first_frame_url"])

        # validate last_frame_url if provided
        if params.get("last_frame_url") is not None:
            self.validate_url("last_frame_url", params["last_frame_url"])

        # validate enable_safety_checker
        if params.get("enable_safety_checker") is not None:
            self.validate_boolean(
                "enable_safety_checker",
                params["enable_safety_checker"]
            )

        # validate enable_prompt_expansion
        if params.get("enable_prompt_expansion") is not None:
            self.validate_boolean(
                "enable_prompt_expansion",
                params["enable_prompt_expansion"]
            )

        # validate sync_mode
        if params.get("sync_mode") is not None:
            self.validate_boolean("sync_mode", params["sync_mode"])

        # validate return_frames_zip
        if params.get("return_frames_zip") is not None:
            self.validate_boolean("return_frames_zip", params["return_frames_zip"])

        return not self.has_errors(), self.get_errors()