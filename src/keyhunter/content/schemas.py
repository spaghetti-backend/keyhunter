from enum import Enum


class ContentType(str, Enum):
    SIMPLE = "Simple text"
    COMMON = "Common words"


class Language(str, Enum):
    ENGLISH = "en"
