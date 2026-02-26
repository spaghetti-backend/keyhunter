from enum import Enum
from typing import NamedTuple


class TyperEngine(str, Enum):
    SINGLE_LINE = "Single line"
    STANDARD = "Standard"


class TyperBorder(str, Enum):
    BLANK = "blank"
    ROUND = "round"
    SOLID = "solid"
    THICK = "thick"
    DOUBLE = "double"
    HEAVY = "heavy"
    HKEY = "hkey"
    TALL = "tall"
    WIDE = "wide"


class Keystroke(NamedTuple):
    key: str
    is_matched: bool
    elapsed_time_ms: int
