from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    computed_field,
    model_validator,
)


class TyperEngine(StrEnum):
    SINGLE_LINE = "Single line"
    STANDARD = "Standard"


class BaseSchema(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class SizeConstraints(BaseSchema):
    width: int = Field(default=80)
    height: int = Field(default=1)
    _min_width: int = PrivateAttr(default=50)
    _max_width: int = PrivateAttr(default=120)
    _min_height: int = PrivateAttr(default=1)
    _max_height: int = PrivateAttr(default=1)

    @computed_field
    @property
    def min_height(self) -> int:
        return self._min_height

    @computed_field
    @property
    def max_height(self) -> int:
        return self._max_height

    @computed_field
    @property
    def min_width(self) -> int:
        return self._min_width

    @computed_field
    @property
    def max_width(self) -> int:
        return self._max_width

    def _clamp(self, v, lo, hi):
        return max(lo, min(v, hi))

    @model_validator(mode="after")
    def clamp_size(self):
        object.__setattr__(
            self, "width", self._clamp(self.width, self.min_width, self.max_width)
        )
        object.__setattr__(
            self, "height", self._clamp(self.height, self.min_height, self.max_height)
        )
        return self


class SingleLineEngineSettings(SizeConstraints):
    enable_pre_content_space: bool = True


class StandardEngineSettings(SizeConstraints):
    height: int = Field(default=5)
    _min_height: int = PrivateAttr(default=3)
    _max_height: int = PrivateAttr(default=9)


class TyperSettings(BaseSchema):
    typer_engine: TyperEngine = Field(default=TyperEngine.SINGLE_LINE)
    border: str | None = "round"
    single_line_engine: SingleLineEngineSettings = Field(
        default_factory=SingleLineEngineSettings
    )
    standard_engine: StandardEngineSettings = Field(
        default_factory=StandardEngineSettings
    )


class AppSettings(BaseSchema):
    theme: str = "textual-dark"
    typer: TyperSettings = Field(default_factory=TyperSettings)
