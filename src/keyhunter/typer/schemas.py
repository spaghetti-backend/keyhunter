from enum import Enum
from typing import NamedTuple


class TyperEngine(str, Enum):
    SINGLE_LINE = "Single line"
    STANDARD = "Standard"


class Keystroke(NamedTuple):
    key: str
    is_matched: bool
    elapsed_time_ms: int
