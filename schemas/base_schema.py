# schemas/base_schema.py
from pydantic import BaseModel

class BaseSchema(BaseModel):

    @classmethod
    def get_required_fields(cls) -> list[str]:
        return [
            name
            for name, field in cls.model_fields.items()
            if field.is_required()
        ]

    @classmethod
    def get_optional_fields(cls) -> list[str]:
        return [
            name
            for name, field in cls.model_fields.items()
            if not field.is_required()
        ]

    @classmethod
    def get_json_schema(cls) -> dict:
        return cls.model_json_schema()