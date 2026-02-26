from abc import ABC, abstractmethod
from typing import Any, Protocol

from keyhunter import const as CONST
from keyhunter.content.schemas import (
    CodeSampleCategory,
    ContentType,
    NaturalLanguage,
    NaturalLanguageCategory,
    ProgrammingLanguage,
    ProgrammingLanguageCategory,
)
from keyhunter.settings.schemas import AppSettings
from keyhunter.typer.schemas import TyperEngine


class SettingChangeCommand(Protocol):
    def __init__(self, value: Any) -> None: ...

    def execute(self, settings: AppSettings) -> None: ...

    def undo(self) -> None: ...


class BaseCommand(ABC):
    def __init__(self, value: Any) -> None:
        self._value = value
        self._old_value = None
        self._settings = None
        self._setting_name = None

    @abstractmethod
    def execute(self, settings: AppSettings) -> None: ...

    def undo(self) -> None:
        if self._settings and self._setting_name and self._old_value:
            setattr(self._settings, self._setting_name, self._old_value)

    def _execute(self, settings, setting_name: str) -> None:
        if self._settings is not None:
            return

        self._settings = settings
        self._setting_name = setting_name
        self._old_value = getattr(settings, setting_name)
        setattr(settings, setting_name, self._value)


#
# App
#
class SetThemeCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(settings, CONST.THEME_KEY)


#
# Typer
#
class SetTyperBorderCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        from keyhunter.settings.schemas import TyperBorder

        self._value = TyperBorder(self._value)
        self._execute(settings.typer, CONST.BORDER_KEY)


class SetTyperEngineCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = TyperEngine(self._value)
        self._execute(settings.typer, CONST.ENGINE_KEY)


class SetSingleLineEngineWidthCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(settings.typer.single_line_engine, CONST.WIDTH_KEY)


class SetSingleLineEngineStartFromCenterCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(
            settings.typer.single_line_engine, CONST.SLE_START_FROM_CENTER_KEY
        )


class SetStandardEngineWidthCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(settings.typer.standard_engine, CONST.WIDTH_KEY)


class SetStandardEngineHeightCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(settings.typer.standard_engine, CONST.HEIGHT_KEY)


#
# Content
#
class SetContentTypeCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = ContentType(self._value)
        self._execute(settings.content, CONST.CONTENT_TYPE_KEY)


class SetNaturalLanguageCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = NaturalLanguage(self._value)
        self._execute(settings.content.natural_language, CONST.LANGUAGE_KEY)


class SetNaturalLanguageCategoryCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = NaturalLanguageCategory(self._value)
        self._execute(settings.content.natural_language, CONST.CATEGORY_KEY)


class SetNaturalLanguageWordsCountCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(
            settings.content.natural_language.common_words, CONST.WORDS_COUNT_KEY
        )


class SetNaturalLanguageContentCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(
            settings.content.natural_language.common_words, CONST.CONTENT_FILES_KEY
        )


class SetProgrammingLanguageCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = ProgrammingLanguage(self._value)
        self._execute(settings.content.programming_language, CONST.LANGUAGE_KEY)


class SetProgrammingLanguageContentTypeCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = ProgrammingLanguageCategory(self._value)
        self._execute(settings.content.programming_language, CONST.CATEGORY_KEY)


class SetProgrammingLanguageKeywordsCountCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._execute(
            settings.content.programming_language.keywords, CONST.KEYWORDS_COUNT_KEY
        )


class SetProgrammingLanguageCodeSampleCommand(BaseCommand):
    def execute(self, settings: AppSettings) -> None:
        self._value = CodeSampleCategory(self._value)
        self._execute(
            settings.content.programming_language.code_samples,
            CONST.CODE_SAMPLE_TYPE_KEY,
        )
