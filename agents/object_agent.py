from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.object_schema import ObjectParams
from validators.object_validator import ObjectValidator

class ObjectAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="object",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return ObjectParams.get_json_schema()

    def get_validator(self):
        return ObjectValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return ObjectParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return ObjectParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(ObjectParams.model_fields.keys())