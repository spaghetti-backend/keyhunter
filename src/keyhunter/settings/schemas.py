from enum import Enum
from typing import Any

from textual.dom import DOMNode
from textual.reactive import reactive

from keyhunter import const as CONST
from keyhunter.content.schemas import (
    CodeSampleCategory,
    NaturalLanguage,
    ContentType,
    NaturalLanguageCategory,
    ProgrammingLanguage,
    ProgrammingLanguageCategory,
)
from keyhunter.typer.schemas import TyperEngine


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


SettingsDict = dict[str, Any]


class BaseSettings(DOMNode):
    def __init__(self):
        super().__init__()
        for base in self.__class__.__bases__:
            self.__annotations__.update(base.__annotations__)

    def dump(self) -> SettingsDict:
        settings = {}
        for setting_name in self.__annotations__:
            setting = getattr(self, setting_name)
            if isinstance(setting, BaseSettings):
                settings[setting_name] = setting.dump()
            else:
                settings[setting_name] = setting

        return settings

    def load(self, settings: SettingsDict, r: bool = True) -> None:
        for setting_name in self.__annotations__:
            setting = getattr(self, setting_name)
            if isinstance(setting, BaseSettings):
                setting.load(settings.get(setting_name, {}))
            else:
                setting_type = type(setting)
                if setting_name not in self._reactives:
                    value = settings.get(setting_name)
                    if value:
                        setattr(self, setting_name, value)

                    return

                reactive_setting = self._reactives[setting_name]
                setting_default = reactive_setting._default
                value = setting_type(settings.get(setting_name, setting_default))
                if r:
                    self.set_reactive(reactive_setting, value)
                else:
                    setattr(self, setting_name, value)


class SizeConstraints(BaseSettings):
    width: reactive[int] = reactive(CONST.SLE_WIDTH, init=False)
    height: reactive[int] = reactive(CONST.SLE_HEIGHT, init=False)

    min_width = CONST.SLE_MIN_WIDTH
    max_width = CONST.SLE_MAX_WIDTH

    min_height = CONST.SLE_MIN_HEIGHT
    max_height = CONST.SLE_MAX_HEIGHT


class SingleLineEngineSettings(SizeConstraints):
    start_from_center: reactive[bool] = reactive(
        CONST.SLE_START_FROM_CENTER, init=False
    )


class StandardEngineSettings(SizeConstraints):
    min_height = CONST.SE_MIN_HEIGHT
    max_height = CONST.SE_MAX_HEIGHT


class TyperSettings(BaseSettings):
    engine: reactive[TyperEngine] = reactive(TyperEngine.SINGLE_LINE, init=False)
    border: reactive[TyperBorder] = reactive(TyperBorder.HKEY, init=False)
    single_line_engine: SingleLineEngineSettings = SingleLineEngineSettings()
    standard_engine: StandardEngineSettings = StandardEngineSettings()


class NaturalLanguageCommonWordsSettings(BaseSettings):
    words_count: reactive[int] = reactive(CONST.WORDS_COUNT, init=False)
    min_words_count = CONST.MIN_WORDS_COUNT
    max_words_count = CONST.MAX_WORDS_COUNT
    content_files: list[str] = list()


class NaturalSimpleTextSettings(BaseSettings): ...


class NaturalLanguageSettings(BaseSettings):
    language: reactive[NaturalLanguage] = reactive(NaturalLanguage.EN, init=False)
    category: reactive[NaturalLanguageCategory] = reactive(
        NaturalLanguageCategory.COMMON, init=False
    )
    common_words: NaturalLanguageCommonWordsSettings = (
        NaturalLanguageCommonWordsSettings()
    )
    simple_text: NaturalSimpleTextSettings = NaturalSimpleTextSettings()


class KeywordsSettings(BaseSettings):
    keywords_count: reactive[int] = reactive(CONST.KEYWORDS_COUNT, init=False)
    min_keywords_count = CONST.MIN_KEYWORDS_COUNT
    max_keywords_count = CONST.MAX_KEYWORDS_COUNT


class CodeSamplesSettings(BaseSettings):
    sample_type: reactive[CodeSampleCategory] = reactive(
        CodeSampleCategory.SIMPLE, init=False
    )


class ProgrammingLanguageSettings(BaseSettings):
    language: reactive = reactive(ProgrammingLanguage.PY, init=False)
    category: reactive[ProgrammingLanguageCategory] = reactive(
        ProgrammingLanguageCategory.KEYWORDS
    )
    keywords: KeywordsSettings = KeywordsSettings()
    code_samples: CodeSamplesSettings = CodeSamplesSettings()


class ContentSettings(BaseSettings):
    content_type: reactive[ContentType] = reactive(ContentType.NATURAL, init=False)
    natural_language: NaturalLanguageSettings = NaturalLanguageSettings()
    programming_language: ProgrammingLanguageSettings = ProgrammingLanguageSettings()


class AppSettings(BaseSettings):
    theme: reactive[str] = reactive(CONST.THEME, init=False)
    typer: TyperSettings = TyperSettings()
    content: ContentSettings = ContentSettings()
