from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.upscaling_schema import UpscalingParams
from validators.upscaling_validator import UpscalingValidator

class UpscalingAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="upscaling",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return UpscalingParams.get_json_schema()

    def get_validator(self):
        return UpscalingValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return UpscalingParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return UpscalingParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(UpscalingParams.model_fields.keys())