from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.lip_sync_schema import LipSyncParams
from validators.lip_sync_validator import LipSyncValidator

class LipSyncAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="lip_sync",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return LipSyncParams.get_json_schema()

    def get_validator(self):
        return LipSyncValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return LipSyncParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return LipSyncParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(LipSyncParams.model_fields.keys())