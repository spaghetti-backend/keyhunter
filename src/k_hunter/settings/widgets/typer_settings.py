from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.widgets import Select, Switch

from k_hunter import const as CONST
from k_hunter.settings.schemas import TyperBorder
from k_hunter.typer.schemas import TyperEngine
from k_hunter.typer.widgets import TyperSimulator

from .components import (
    LinearSlider,
    LinearSliderSetting,
    SelectSetting,
    SwitchSetting,
)

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class TyperEngineSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_engine = self.app.settings.typer.engine
        available_engines = [engine.value for engine in TyperEngine]
        yield SelectSetting(
            id="typer_engine",
            label="Typer engine",
            values=available_engines,
            default=current_engine,
            target=self.app.settings.typer,
            attr_name=CONST.ENGINE_KEY,
            cast=TyperEngine,
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
            id="typer_border",
            label="Border",
            values=available_borders,
            default=current_border,
            target=self.app.settings.typer,
            attr_name=CONST.BORDER_KEY,
            cast=TyperBorder,
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
            id="sle-width",
            label="Width",
            target=self.app.settings.typer.single_line_engine,
            attr_name=CONST.WIDTH_KEY,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.single_line_engine,
            CONST.WIDTH_KEY,
            self._on_single_line_engine_width_changed,
            init=False,
        )

    def _on_single_line_engine_width_changed(self, width: int) -> None:
        with self.prevent(LinearSlider.Changed):
            self.query_one(LinearSlider).set_value(width)


class SingleLineEngineStartFromCenterSwitch(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_choice = self.app.settings.typer.single_line_engine.start_from_center
        yield SwitchSetting(
            id="sle_start_from_center",
            label="Start from center",
            default=current_choice,
            target=self.app.settings.typer.single_line_engine,
            attr_name=CONST.SLE_START_FROM_CENTER_KEY,
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
            id="se-width",
            label="Width",
            target=self.app.settings.typer.standard_engine,
            attr_name=CONST.WIDTH_KEY,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.standard_engine,
            CONST.WIDTH_KEY,
            self._on_standard_engine_width_changed,
            init=False,
        )

    def _on_standard_engine_width_changed(self, width: int) -> None:
        with self.prevent(LinearSlider.Changed):
            self.query_one(LinearSlider).set_value(width)


class StandardEngineHeight(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.typer.standard_engine
        yield LinearSliderSetting(
            positions_count=CONST.SE_HEIGHT_STEPS,
            current_value=settings.height,
            min_value=settings.min_height,
            max_value=settings.max_height,
            id="se-height",
            label="Height",
            target=self.app.settings.typer.standard_engine,
            attr_name=CONST.HEIGHT_KEY,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.typer.standard_engine,
            CONST.HEIGHT_KEY,
            self._on_standard_engine_height_changed,
            init=False,
        )

    def _on_standard_engine_height_changed(self, height: int) -> None:
        with self.prevent(LinearSlider.Changed):
            self.query_one(LinearSlider).set_value(height)


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

        with Center():
            yield TyperSimulator(self.app.settings)

    def on_mount(self) -> None:
        self.query_exactly_one(TyperSimulator).simulate()

    def on_show(self) -> None:
        self.query_exactly_one(TyperSimulator).resume()

    def on_hide(self) -> None:
        self.query_exactly_one(TyperSimulator).pause()
