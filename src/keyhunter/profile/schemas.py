from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=True)


class TypingSummary(BaseSchema):
    elapsed_time: float = Field(default=0.0, ge=0.0)
    total_chars: int = Field(default=0, ge=0)
    correct_chars: int = Field(default=0, ge=0)
