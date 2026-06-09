from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.background_schema import BackgroundParams
from validators.background_validator import BackgroundValidator

class BackgroundAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="background",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return BackgroundParams.get_json_schema()

    def get_validator(self):
        return BackgroundValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return BackgroundParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return BackgroundParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(BackgroundParams.model_fields.keys())