from typing import Any, Literal

from textual.dom import DOMNode
from textual.reactive import reactive

from keyhunter.content.schemas import ContentType, Language
from keyhunter.settings.commands import SettingChangeCommand
from keyhunter.settings.storage import SettingsStorage
from keyhunter.typer.schemas import TyperEngine

TyperBorder = Literal[
    "blank", "round", "solid", "thick", "double", "heavy", "hkey", "tall", "wide"
]

SettingsDict = dict[str, Any]


class SizeConstraints(DOMNode):
    _width: reactive[int] = reactive(50, init=False)
    _height: reactive[int] = reactive(1, init=False)

    _min_width = 50
    _max_width = 120

    _min_height = 1
    _max_height = 1

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _apply_settings(self, settings: SettingsDict) -> None:
        width = settings.get("width")
        if width:
            self.set_reactive(self.__class__._width, width)
        else:
            self._width = self._min_width

        height = settings.get("height")
        if height:
            self.set_reactive(self.__class__._height, height)
        else:
            self._height = self._min_height

    def _dump_settings(self) -> SettingsDict:
        return {
            "width": self._width,
            "height": self._height,
        }


class SingleLineEngineSettings(SizeConstraints):
    _start_from_center: reactive[bool] = reactive(True, init=False)

    @property
    def start_from_center(self) -> bool:
        return self._start_from_center

    def _apply_settings(self, settings: SettingsDict) -> None:
        super()._apply_settings(settings)

        start_from_center = settings.get("start_from_center")
        if start_from_center is not None:
            self.set_reactive(self.__class__._start_from_center, start_from_center)
        else:
            self._start_from_center = True

    def _dump_settings(self) -> SettingsDict:
        size_settings = super()._dump_settings()
        return {
            "start_from_center": self._start_from_center,
            **size_settings,
        }


class StandardEngineSettings(SizeConstraints):
    _min_height = 3
    _max_height = 9


class TyperSettings(DOMNode):
    _engine: reactive[TyperEngine] = reactive(TyperEngine.SINGLE_LINE, init=False)
    _border: reactive[TyperBorder] = reactive("round", init=False)
    _single_line_engine: SingleLineEngineSettings = SingleLineEngineSettings()
    _standard_engine: StandardEngineSettings = StandardEngineSettings()

    @property
    def engine(self) -> TyperEngine:
        return self._engine

    @property
    def border(self) -> TyperBorder:
        return self._border

    @property
    def single_line_engine(self) -> SingleLineEngineSettings:
        return self._single_line_engine

    @property
    def standard_engine(self) -> StandardEngineSettings:
        return self._standard_engine

    def _apply_settings(self, settings: SettingsDict) -> None:
        engine = settings.get("engine")
        if engine:
            self.set_reactive(self.__class__._engine, TyperEngine(engine))
        else:
            self._engine = TyperEngine.SINGLE_LINE

        border = settings.get("border")
        if border:
            self.set_reactive(self.__class__._border, border)
        else:
            self._border = "hkey"

        self._standard_engine._apply_settings(settings.get("standard_engine", {}))
        self._single_line_engine._apply_settings(settings.get("single_line_engine", {}))

    def _dump_settings(self) -> SettingsDict:
        return {
            "engine": self._engine.value,
            "border": self._border,
            "single_line_engine": self._single_line_engine._dump_settings(),
            "standard_engine": self._standard_engine._dump_settings(),
        }


class ContentSettings(DOMNode):
    _language: reactive[Language] = reactive(Language.ENGLISH, init=False)
    _content_type: reactive[ContentType] = reactive(ContentType.COMMON, init=False)
    _content_lenght: reactive[int] = reactive(20, init=False)
    _min_content_lenght = 20
    _max_content_lenght = 1000

    @property
    def language(self) -> Language:
        return self._language

    @property
    def content_type(self) -> ContentType:
        return self._content_type

    @property
    def content_lenght(self) -> int:
        return self._content_lenght

    def _apply_settings(self, settings: SettingsDict) -> None:
        language = settings.get("language")
        if language:
            self.set_reactive(self.__class__._language, Language(language))
        else:
            self._language = Language.ENGLISH

        content_type = settings.get("content_type")
        if content_type:
            self.set_reactive(self.__class__._content_type, ContentType(content_type))
        else:
            self._content_type = ContentType.COMMON

        content_lenght = settings.get("content_lenght")
        if content_lenght:
            self.set_reactive(self.__class__._content_lenght, content_lenght)
        else:
            self._content_lenght = 20

    def _dump_settings(self) -> SettingsDict:
        return {
            "language": self._language.value,
            "content_type": self._content_type.value,
            "content_lenght": self._content_lenght,
        }


class AppSettings(DOMNode):
    _theme: reactive[str] = reactive("nord", init=False)
    _typer: TyperSettings = TyperSettings()
    _content: ContentSettings = ContentSettings()

    def __init__(self) -> None:
        super().__init__()
        self._history: list[SettingChangeCommand] = []
        self._storage = SettingsStorage()

        settings = self._storage.load()
        self._apply_settings(settings)

    @property
    def theme(self) -> str:
        return self._theme

    @property
    def typer(self) -> TyperSettings:
        return self._typer

    @property
    def content(self) -> ContentSettings:
        return self._content

    def update(self, command: SettingChangeCommand):
        command.execute(self)
        self._history.append(command)
        self.save()

    def reset_to_default(self) -> None:
        self._apply_settings({})

    def save(self) -> None:
        self._storage.save(self._dump_settings())

    def _apply_settings(self, settings: SettingsDict) -> None:
        self._theme = settings.get("theme", "textual-dark")

        self._typer._apply_settings(settings.get("typer", {}))
        self._content._apply_settings(settings.get("content", {}))

    def _dump_settings(self) -> SettingsDict:
        return {
            "theme": self._theme,
            "typer": self._typer._dump_settings(),
            "content": self._content._dump_settings(),
        }
