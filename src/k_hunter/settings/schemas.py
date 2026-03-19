from typing import Any
import inspect

from textual.dom import DOMNode
from textual.reactive import reactive

from k_hunter import const as CONST
from k_hunter.content.schemas import (
    CodeSampleCategory,
    ContentType,
    NaturalLanguage,
    NaturalLanguageCategory,
    ProgrammingLanguage,
    ProgrammingLanguageCategory,
)
from k_hunter.typer.schemas import TyperBorder, TyperEngine

SettingsDict = dict[str, Any]


class BaseSettings(DOMNode):
    def __init__(self):
        super().__init__()
        self._annotations = inspect.get_annotations(type(self))
        for base in self.__class__.__bases__:
            self._annotations.update(inspect.get_annotations(base))

    def dump(self) -> SettingsDict:
        settings = {}
        for setting_name in self._annotations:
            setting = getattr(self, setting_name)
            if isinstance(setting, BaseSettings):
                settings[setting_name] = setting.dump()
            else:
                settings[setting_name] = setting

        return settings

    def load(self, settings: SettingsDict, set_reactive: bool = True) -> None:
        for setting_name in self._annotations:
            setting = getattr(self, setting_name)

            if isinstance(setting, BaseSettings):
                setting.load(settings.get(setting_name, {}), set_reactive=set_reactive)
            else:
                setting_type = type(setting)
                if setting_name not in self._reactives:
                    value = settings.get(setting_name)
                    if value is not None:
                        setattr(self, setting_name, value)

                    continue

                reactive_setting = self._reactives[setting_name]
                setting_default = reactive_setting._default
                value = setting_type(settings.get(setting_name, setting_default))
                if set_reactive:
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
    height: reactive[int] = reactive(CONST.SE_HEIGHT, init=False)
    min_height = CONST.SE_MIN_HEIGHT
    max_height = CONST.SE_MAX_HEIGHT


class TyperSettings(BaseSettings):
    engine: reactive[TyperEngine] = reactive(TyperEngine.STANDARD, init=False)
    border: reactive[TyperBorder] = reactive(TyperBorder.HKEY, init=False)
    single_line_engine: SingleLineEngineSettings = SingleLineEngineSettings()
    standard_engine: StandardEngineSettings = StandardEngineSettings()


class NaturalLanguageCommonWordsSettings(BaseSettings):
    words_count: reactive[int] = reactive(CONST.WORDS_COUNT, init=False)
    min_words_count = CONST.MIN_WORDS_COUNT
    max_words_count = CONST.MAX_WORDS_COUNT

    upper_percent: reactive[int] = reactive(CONST.UPPER_PERCENT, init=False)
    min_upper_percent: reactive[int] = reactive(CONST.MIN_UPPER_PERCENT, init=False)
    max_upper_percent: reactive[int] = reactive(CONST.MAX_UPPER_PERCENT, init=False)

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
    content_files: list[str] = list()


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
