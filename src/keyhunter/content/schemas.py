from enum import Enum


class ContentType(str, Enum):
    NATURAL = "Natural language"
    PRAGRAMMING = "Programming language"


class NaturalLanguage(str, Enum):
    EN = "English"


class NaturalLanguageCategory(str, Enum):
    SIMPLE = "Simple text"
    COMMON = "Common words"


class ProgrammingLanguage(str, Enum):
    PY = "Python"


class ProgrammingLanguageCategory(str, Enum):
    KEYWORDS = "Keywords"
    CODE = "Code samples"


class CodeSampleCategory(str, Enum):
    SIMPLE = "Simple code"
