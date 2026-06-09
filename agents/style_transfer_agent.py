from agents.base_agent import BaseAgent
from state.shared_state import SharedState
from schemas.style_transfer_schema import StyleTransferParams
from validators.style_transfer_validator import StyleTransferValidator

class StyleTransferAgent(BaseAgent):

    def __init__(self, shared_state: SharedState):
        super().__init__(
            feature_name="style_transfer",
            shared_state=shared_state
        )

    def get_schema(self) -> dict:
        return StyleTransferParams.get_json_schema()

    def get_validator(self):
        return StyleTransferValidator(self.video_metadata)

    def get_required_fields(self) -> list[str]:
        return StyleTransferParams.get_required_fields()

    def get_optional_fields(self) -> list[str]:
        return StyleTransferParams.get_optional_fields()

    def get_valid_keys(self) -> set[str]:
        return set(StyleTransferParams.model_fields.keys())