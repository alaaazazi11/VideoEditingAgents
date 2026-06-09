from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.extend_duration_schema import ExtendDurationParams
from validators.extend_duration_validator import ExtendDurationValidator

class ExtendDurationAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="extend_duration",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return ExtendDurationParams.get_json_schema()

    def get_validator(self):
        return ExtendDurationValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return ExtendDurationParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return ExtendDurationParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(ExtendDurationParams.model_fields.keys())