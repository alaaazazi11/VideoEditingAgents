from .base_validator import BaseValidator, ValidationError


class KlingValidator(BaseValidator):

    def __init__(self, video_metadata: dict):
        super().__init__(video_metadata)

    def validate(self, params: dict) -> tuple[bool, list[ValidationError]]:
        self.clear_errors()

        # validate video_url
        if "video_url" in params:
            self.validate_url("video_url", params["video_url"])

        # validate prompt
        if "prompt" in params:
            self.validate_string("prompt", params["prompt"])

        # validate image_urls
        if params.get("image_urls") is not None:
            if not isinstance(params["image_urls"], list):
                self.errors.append(ValidationError(
                    param="image_urls",
                    reason="image_urls must be a list of URLs",
                ))
            else:
                for i, url in enumerate(params["image_urls"]):
                    self.validate_url(f"image_urls[{i}]", url)

        # validate keep_audio
        if "keep_audio" in params:
            self.validate_boolean("keep_audio", params["keep_audio"])

        # validate elements
        if params.get("elements") is not None:
            if not isinstance(params["elements"], list):
                self.errors.append(ValidationError(
                    param="elements",
                    reason="elements must be a list",
                ))
            else:
                for i, element in enumerate(params["elements"]):
                    if "image_url" not in element:
                        self.errors.append(ValidationError(
                            param=f"elements[{i}].image_url",
                            reason="each element must have an image_url",
                        ))
                    else:
                        self.validate_url(f"elements[{i}].image_url", element["image_url"])

        return not self.has_errors(), self.get_errors()