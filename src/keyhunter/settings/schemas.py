from enum import Enum
from typing import Any

from textual.dom import DOMNode
from textual.reactive import reactive

from keyhunter import const as CONST
from keyhunter.content.schemas import ContentLanguage, ContentType
from keyhunter.settings.commands import SettingChangeCommand
from keyhunter.settings.storage import SettingsStorage
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


class SizeConstraints(DOMNode):
    _width: reactive[int] = reactive(CONST.SLE_WIDTH, init=False)
    _height: reactive[int] = reactive(CONST.SLE_HEIGHT, init=False)

    _min_width = CONST.SLE_MIN_WIDTH
    _max_width = CONST.SLE_MAX_WIDTH

    _min_height = CONST.SLE_MIN_HEIGHT
    _max_height = CONST.SLE_MAX_HEIGHT

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _apply_settings(self, settings: SettingsDict) -> None:
        width = settings.get(CONST.WIDTH_KEY)
        if width:
            self.set_reactive(self.__class__._width, width)
        else:
            self._width = self._min_width

        height = settings.get(CONST.HEIGHT_KEY)
        if height:
            self.set_reactive(self.__class__._height, height)
        else:
            self._height = self._min_height

    def _dump_settings(self) -> SettingsDict:
        return {
            CONST.WIDTH_KEY: self._width,
            CONST.HEIGHT_KEY: self._height,
        }


class SingleLineEngineSettings(SizeConstraints):
    _start_from_center: reactive[bool] = reactive(
        CONST.SLE_START_FROM_CENTER, init=False
    )

    @property
    def start_from_center(self) -> bool:
        return self._start_from_center

    def _apply_settings(self, settings: SettingsDict) -> None:
        super()._apply_settings(settings)

        start_from_center = settings.get(CONST.SLE_START_FROM_CENTER_KEY)
        if start_from_center is not None:
            self.set_reactive(self.__class__._start_from_center, start_from_center)
        else:
            self._start_from_center = True

    def _dump_settings(self) -> SettingsDict:
        size_settings = super()._dump_settings()
        return {
            CONST.SLE_START_FROM_CENTER_KEY: self._start_from_center,
            **size_settings,
        }


class StandardEngineSettings(SizeConstraints):
    _min_height = CONST.SE_MIN_HEIGHT
    _max_height = CONST.SE_MAX_HEIGHT


class TyperSettings(DOMNode):
    _engine: reactive[TyperEngine] = reactive(TyperEngine.SINGLE_LINE, init=False)
    _border: reactive[TyperBorder] = reactive(TyperBorder.HKEY, init=False)
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
        engine = settings.get(CONST.ENGINE_KEY)
        if engine:
            self.set_reactive(self.__class__._engine, TyperEngine(engine))
        else:
            self._engine = TyperEngine.SINGLE_LINE

        border = settings.get(CONST.BORDER_KEY)
        if border:
            self.set_reactive(self.__class__._border, TyperBorder(border))
        else:
            self._border = TyperBorder.HKEY

        self._standard_engine._apply_settings(settings.get(CONST.SE_KEY, {}))
        self._single_line_engine._apply_settings(settings.get(CONST.SLE_KEY, {}))

    def _dump_settings(self) -> SettingsDict:
        return {
            CONST.ENGINE_KEY: self._engine.value,
            CONST.BORDER_KEY: self._border.value,
            CONST.SLE_KEY: self._single_line_engine._dump_settings(),
            CONST.SE_KEY: self._standard_engine._dump_settings(),
        }


class ContentSettings(DOMNode):
    _language: reactive[ContentLanguage] = reactive(ContentLanguage.EN, init=False)
    _content_type: reactive[ContentType] = reactive(ContentType.COMMON, init=False)
    _content_lenght: reactive[int] = reactive(CONST.CONTENT_LENGHT, init=False)
    _min_content_lenght = CONST.CONTENT_MIN_LENGHT
    _max_content_lenght = CONST.CONTENT_MAX_LENGHT

    @property
    def language(self) -> ContentLanguage:
        return self._language

    @property
    def content_type(self) -> ContentType:
        return self._content_type

    @property
    def content_lenght(self) -> int:
        return self._content_lenght

    def _apply_settings(self, settings: SettingsDict) -> None:
        language = settings.get(CONST.LANGUAGE_KEY)
        if language:
            self.set_reactive(self.__class__._language, ContentLanguage(language))
        else:
            self._language = ContentLanguage.EN

        content_type = settings.get(CONST.CONTENT_TYPE_KEY)
        if content_type:
            self.set_reactive(self.__class__._content_type, ContentType(content_type))
        else:
            self._content_type = ContentType.COMMON

        content_lenght = settings.get(CONST.CONTENT_LENGHT_KEY)
        if content_lenght:
            self.set_reactive(self.__class__._content_lenght, content_lenght)
        else:
            self._content_lenght = CONST.CONTENT_LENGHT

    def _dump_settings(self) -> SettingsDict:
        return {
            CONST.LANGUAGE_KEY: self._language.value,
            CONST.CONTENT_TYPE_KEY: self._content_type.value,
            CONST.CONTENT_LENGHT_KEY: self._content_lenght,
        }


class AppSettings(DOMNode):
    _theme: reactive[str] = reactive(CONST.THEME, init=False)
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
        self._theme = settings.get(CONST.THEME_KEY, CONST.THEME)

        self._typer._apply_settings(settings.get(CONST.TYPER_KEY, {}))
        self._content._apply_settings(settings.get(CONST.CONTENT_KEY, {}))

    def _dump_settings(self) -> SettingsDict:
        return {
            CONST.THEME_KEY: self._theme,
            CONST.TYPER_KEY: self._typer._dump_settings(),
            CONST.CONTENT_KEY: self._content._dump_settings(),
        }
