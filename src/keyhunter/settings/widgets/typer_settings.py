from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.validation import Number
from textual.widgets import Input, Select, Switch

from keyhunter.settings.commands import (
    SetSingleLineEngineStartFromCenterCommand,
    SetSingleLineEngineWidthCommand,
    SetStandardEngineHeightCommand,
    SetStandardEngineWidthCommand,
    SetTyperBorderCommand,
    SetTyperEngineCommand,
)
from keyhunter.settings.schemas import TyperBorder
from keyhunter.typer.schemas import TyperEngine

from .components import (
    InputSetting,
    SelectSetting,
    SwitchSetting,
)

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class TyperEngineSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_engine = self.app.settings.typer.engine.value
        available_engines = [engine.value for engine in TyperEngine]
        yield SelectSetting(
            command=SetTyperEngineCommand,
            id="typer_engine",
            label="Typer engine",
            values=available_engines,
            default=current_engine,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer,
            "_engine",
            self._on_typer_engine_changed,
            init=False,
        )

    def _on_typer_engine_changed(self, engine: TyperEngine) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = engine


class TyperBorderSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_border = self.app.settings.typer.border
        available_borders = list(TyperBorder.__args__)
        yield SelectSetting(
            command=SetTyperBorderCommand,
            id="typer_border",
            label="Border",
            values=available_borders,
            default=current_border,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer,
            "_border",
            self._on_typer_border_changed,
            init=False,
        )

    def _on_typer_border_changed(self, border: TyperBorder) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = border


class SingleLineEngineWidth(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        sle_settings = self.app.settings.typer.single_line_engine
        current_width = sle_settings.width
        width_validator = Number(
            minimum=sle_settings._min_width,
            maximum=sle_settings._max_width,
        )
        yield InputSetting(
            command=SetSingleLineEngineWidthCommand,
            id="sle_width",
            label="Width",
            default=current_width,
            validators=[width_validator],
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.single_line_engine,
            "_width",
            self._on_sle_width_changed,
            init=False,
        )

    def _on_sle_width_changed(self, width: int) -> None:
        with self.prevent(Input.Changed):
            self.query_one(Input).value = str(width)


class SingleLineEngineStartFromCenterSwitch(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_choice = self.app.settings.typer.single_line_engine.start_from_center
        yield SwitchSetting(
            command=SetSingleLineEngineStartFromCenterCommand,
            id="sle_start_from_center",
            label="Start from center",
            default=current_choice,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.single_line_engine,
            "_start_from_center",
            self._on_sle_start_from_center_changed,
            init=False,
        )

    def _on_sle_start_from_center_changed(self, start_from_center: bool) -> None:
        with self.prevent(Switch.Changed):
            self.query_one(Switch).value = start_from_center


class StandardEngineWidth(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        se_settings = self.app.settings.typer.standard_engine
        current_width = se_settings.width
        width_validator = Number(
            minimum=se_settings._min_width,
            maximum=se_settings._max_width,
        )
        yield InputSetting(
            command=SetStandardEngineWidthCommand,
            id="se_width",
            label="Width",
            default=current_width,
            validators=[width_validator],
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.standard_engine,
            "_width",
            self._on_se_width_changed,
            init=False,
        )

    def _on_se_width_changed(self, width: int) -> None:
        with self.prevent(Input.Changed):
            self.query_one(Input).value = str(width)


class StandardEngineHeight(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        se_settings = self.app.settings.typer.standard_engine
        current_height = se_settings.height
        height_validator = Number(
            minimum=se_settings._min_height,
            maximum=se_settings._max_height,
        )
        yield InputSetting(
            command=SetStandardEngineHeightCommand,
            id="se_height",
            label="Height",
            default=current_height,
            validators=[height_validator],
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.standard_engine,
            "_height",
            self._on_se_height_changed,
            init=False,
        )

    def _on_se_height_changed(self, height: int) -> None:
        with self.prevent(Input.Changed):
            self.query_one(Input).value = str(height)


class SingleLineEngineSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    BORDER_TITLE = "Single line engine"

    def compose(self) -> ComposeResult:
        yield SingleLineEngineWidth(classes="setting-container")
        yield SingleLineEngineStartFromCenterSwitch(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer, "_engine", self._toggle_container_visibility
        )

    def _toggle_container_visibility(self, typer_engine: TyperEngine) -> None:
        if typer_engine == TyperEngine.SINGLE_LINE:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class StandardEngineSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    BORDER_TITLE = "Standard engine"

    def compose(self) -> ComposeResult:
        yield StandardEngineWidth(classes="setting-container")
        yield StandardEngineHeight(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer, "_engine", self._toggle_container_visibility
        )

    def _toggle_container_visibility(self, typer_engine: TyperEngine) -> None:
        if typer_engine == TyperEngine.STANDARD:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class TyperSettingsContainer(VerticalGroup):
    BORDER_TITLE = "Typer"

    def compose(self) -> ComposeResult:
        yield TyperEngineSelector(classes="setting-container")
        yield TyperBorderSelector(classes="setting-container")
