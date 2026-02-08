from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, computed_field

MILLISECONDS_MULTIPLIER = 1000


class BaseSchema(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=True)


class Keystroke(BaseSchema):
    key: str
    is_matched: bool
    elapsed_time_ms: int = Field(default=0, ge=0)


class TypingSessionSummary(BaseSchema):
    elapsed_time_ms: int = Field(default=0, ge=0)
    total_chars: int = Field(default=0, ge=0)
    correct_chars: int = Field(default=0, ge=0)
    keystrokes: list[Keystroke]

    @computed_field
    @property
    def accuracy(self) -> str:
        if not self._is_typing_summary_present():
            return "N/A"

        typing_accuracy = round((self.correct_chars / self.total_chars) * 100, 2)
        return f"{typing_accuracy}%"

    @computed_field
    @property
    def speed(self) -> str:
        if not self._is_typing_summary_present():
            return "N/A"

        minutes = self.elapsed_time_ms / (60 * MILLISECONDS_MULTIPLIER)
        cpm = round(self.total_chars / minutes, 2)
        return f"{cpm}cpm"

    @computed_field
    @property
    def time(self) -> str:
        delta = timedelta(milliseconds=self.elapsed_time_ms)
        dt = datetime.min + delta
        return dt.strftime("%M:%S")

    def _is_typing_summary_present(self) -> bool:
        return bool(self.total_chars and self.elapsed_time_ms)
