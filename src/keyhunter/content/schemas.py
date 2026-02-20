from enum import Enum


class ContentType(str, Enum):
    SIMPLE = "Simple text"
    COMMON = "Common words"


class ContentLanguage(str, Enum):
    EN = "English"
