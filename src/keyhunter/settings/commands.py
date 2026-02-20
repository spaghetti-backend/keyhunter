from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol

from keyhunter.content.schemas import ContentType, Language
from keyhunter.typer.schemas import TyperEngine


if TYPE_CHECKING:
    from keyhunter.settings.schemas import AppSettings


class SettingChangeCommand(Protocol):
    def __init__(self, value: Any) -> None: ...

    def execute(self, settings: "AppSettings") -> None: ...

    def undo(self) -> None: ...


class BaseCommand(ABC):
    def __init__(self, value: Any) -> None:
        self._value = value
        self._old_value = None
        self._settings = None
        self._setting_name = None

    @abstractmethod
    def execute(self, settings: "AppSettings") -> None: ...

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


class SetThemeCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings, "_theme")


class SetTyperBorderCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.typer, "_border")


class SetTyperEngineCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._value = TyperEngine(self._value)
        self._execute(settings.typer, "_engine")


class SetSingleLineEngineWidthCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.typer.single_line_engine, "_width")


class SetSingleLineEngineStartFromCenterCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.typer.single_line_engine, "_start_from_center")


class SetStandardEngineWidthCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.typer.standard_engine, "_width")


class SetStandardEngineHeightCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.typer.standard_engine, "_height")


class SetContentLanguageCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._value = Language(self._value)
        self._execute(settings.content, "_language")


class SetContentTypeCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._value = ContentType(self._value)
        self._execute(settings.content, "_content_type")


class SetContentLenghtCommand(BaseCommand):
    def execute(self, settings: "AppSettings") -> None:
        self._execute(settings.content, "_content_lenght")
