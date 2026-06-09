import re
import httpx
from typing import Any, Optional
from pydantic import BaseModel

class ValidationError(BaseModel):
    param: str
    reason: str
    valid_options: Optional[list[Any]] = None

class BaseValidator:
    
    def __init__(self, video_metadata: dict):
        self.video_metadata = video_metadata
        self.errors: list[ValidationError] = []

    def validate_url(self, param: str, value: str) -> bool:
        """Validate that a value is a valid URL"""
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        if not url_pattern.match(value):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is not a valid URL",
            ))
            return False
        return True

    def validate_video_url(self, param: str, value: str) -> bool:
        """Validate video URL format, duration and size using shared state metadata"""
        if not self.validate_url(param, value):
            return False

        errors = []

        # validate format
        allowed_formats = ["mp4", "mov"]
        video_format = self.video_metadata.get("format", "").lower()
        if video_format not in allowed_formats:
            errors.append(ValidationError(
                param=param,
                reason=f"Video format '{video_format}' is not supported. Must be MP4 or MOV",
                valid_options=["MP4", "MOV"],
            ))

        # validate duration
        duration = self.video_metadata.get("duration", 0)
        if not (2 <= duration <= 10):
            errors.append(ValidationError(
                param=param,
                reason=f"Video duration is {duration}s. Must be between 2-10 seconds",
            ))

        # validate size
        size_mb = self.video_metadata.get("size_mb", 0)
        if size_mb > 100:
            errors.append(ValidationError(
                param=param,
                reason=f"Video size is {size_mb:.1f}MB. Must be under 100MB",
            ))

        if errors:
            self.errors.extend(errors)
            return False
        return True

    def validate_enum(self, param: str, value: Any, valid_options: list[Any]) -> bool:
        """Validate that a value is one of the accepted enum values"""
        if value not in valid_options:
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is not a valid value for {param}",
                valid_options=valid_options,
            ))
            return False
        return True

    def validate_integer_range(self, param: str, value: int, min_val: int, max_val: int) -> bool:
        """Validate that an integer is within a range"""
        if not isinstance(value, int):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' must be an integer",
            ))
            return False
        if not (min_val <= value <= max_val):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is out of range. Must be between {min_val} and {max_val}",
            ))
            return False
        return True

    def validate_float_range(self, param: str, value: float, min_val: float, max_val: float) -> bool:
        """Validate that a float is within a range"""
        if not isinstance(value, (int, float)):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' must be a number",
            ))
            return False
        if not (min_val <= value <= max_val):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is out of range. Must be between {min_val} and {max_val}",
            ))
            return False
        return True

    def validate_boolean(self, param: str, value: Any) -> bool:
        """Validate that a value is a boolean"""
        if not isinstance(value, bool):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' must be true or false",
                valid_options=[True, False],
            ))
            return False
        return True

    def validate_string(self, param: str, value: Any) -> bool:
        """Validate that a value is a non-empty string"""
        if not isinstance(value, str) or not value.strip():
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{param}' must be a non-empty string",
            ))
            return False
        return True

    def validate_keyframe_id(self, param: str, value: int) -> bool:
        """Validate keyframe_id against video duration from shared state"""
        duration = self.video_metadata.get("duration", 0)
        max_keyframe = int(duration * 24)
        if not (1 <= value <= max_keyframe):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is out of range. Must be between 1 and {max_keyframe} (video duration {duration}s x 24 FPS)",
            ))
            return False
        return True

    def validate_context(self, param: str, value: float) -> bool:
        """Validate context against video duration from shared state"""
        duration = self.video_metadata.get("duration", 0)
        if not (1 <= value <= min(20, duration)):
            self.errors.append(ValidationError(
                param=param,
                reason=f"'{value}' is out of range. Must be between 1 and {min(20, duration)} seconds (capped at video duration)",
            ))
            return False
        return True

    def get_errors(self) -> list[ValidationError]:
        return self.errors

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def clear_errors(self):
        self.errors = []