from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widgets import Select, Switch

from keyhunter import const as CONST
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
from keyhunter.typer.simulator import TyperSimulator

from .components import (
    LinearSliderSetting,
    SelectSetting,
    SwitchSetting,
)

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class TyperEngineSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_engine = self.app.settings.typer.engine
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
            CONST.ENGINE_KEY,
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
        available_borders = [border.value for border in TyperBorder]
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
            CONST.BORDER_KEY,
            self._on_typer_border_changed,
            init=False,
        )

    def _on_typer_border_changed(self, border: TyperBorder) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = border


class SingleLineEngineWidth(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.typer.single_line_engine
        yield LinearSliderSetting(
            positions_count=CONST.SLE_WIDTH_STEPS,
            current_value=settings.width,
            min_value=settings.min_width,
            max_value=settings.max_width,
            command=SetSingleLineEngineWidthCommand,
            id="sle-width",
            label="Width",
        )


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
            CONST.SLE_START_FROM_CENTER_KEY,
            self._on_sle_start_from_center_changed,
            init=False,
        )

    def _on_sle_start_from_center_changed(self, start_from_center: bool) -> None:
        with self.prevent(Switch.Changed):
            self.query_one(Switch).value = start_from_center


class StandardEngineWidth(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.typer.standard_engine
        yield LinearSliderSetting(
            positions_count=CONST.SE_WIDTH_STEPS,
            current_value=settings.width,
            min_value=settings.min_width,
            max_value=settings.max_width,
            command=SetStandardEngineWidthCommand,
            id="se-width",
            label="Width",
        )


class StandardEngineHeight(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.typer.standard_engine
        yield LinearSliderSetting(
            positions_count=CONST.SE_HEIGHT_STEPS,
            current_value=settings.height,
            min_value=settings.min_height,
            max_value=settings.max_height,
            command=SetStandardEngineHeightCommand,
            id="se-height",
            label="Height",
        )


class SingleLineEngineSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield SingleLineEngineWidth(classes="setting-container")
        yield SingleLineEngineStartFromCenterSwitch(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer, CONST.ENGINE_KEY, self._toggle_container_visibility
        )

    def _toggle_container_visibility(self, typer_engine: TyperEngine) -> None:
        if typer_engine == TyperEngine.SINGLE_LINE:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class StandardEngineSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield StandardEngineWidth(classes="setting-container")
        yield StandardEngineHeight(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer, CONST.ENGINE_KEY, self._toggle_container_visibility
        )

    def _toggle_container_visibility(self, typer_engine: TyperEngine) -> None:
        if typer_engine == TyperEngine.STANDARD:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class TyperSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    BORDER_TITLE = "Typer"

    def compose(self) -> ComposeResult:
        yield TyperEngineSelector(classes="setting-container")
        yield TyperBorderSelector(classes="setting-container")

        yield SingleLineEngineSettingsContainer()
        yield StandardEngineSettingsContainer()

        self.typer = TyperSimulator(self.app.settings)
        self.typer.simulate()
        with Center():
            yield self.typer

    def on_show(self) -> None:
        self.typer.resume()

    def on_hide(self) -> None:
        self.typer.pause()
