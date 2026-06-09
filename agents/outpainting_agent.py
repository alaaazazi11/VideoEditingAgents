from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.outpainting_schema import OutpaintingParams
from validators.outpainting_validator import OutpaintingValidator

class OutpaintingAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="outpainting",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return OutpaintingParams.get_json_schema()

    def get_validator(self):
        return OutpaintingValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return OutpaintingParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return OutpaintingParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(OutpaintingParams.model_fields.keys())