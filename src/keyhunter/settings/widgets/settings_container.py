from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
from textual.events import DescendantFocus
from textual.reactive import reactive

from keyhunter.settings.schemas import AppSettings
from keyhunter.settings.widgets.app_settings import AppSettingsContainer
from keyhunter.settings.widgets.content_settings import ContentSettingsContainer
from keyhunter.settings.widgets.typer_settings import (
    SingleLineEngineSettingsContainer,
    StandardEngineSettingsContainer,
    TyperSettingsContainer,
)
from keyhunter.typer.simulator import TyperSimulator


class SettingsContainer(VerticalScroll, can_focus=True):
    _is_active: reactive[bool] = reactive(False, init=False)
    _last_focused = None

    def __init__(self, settings: AppSettings, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._settings = settings

    def compose(self) -> ComposeResult:
        yield AppSettingsContainer(classes="settings-group-container")
        yield TyperSettingsContainer(classes="settings-group-container")

        typer = TyperSimulator(self._settings)
        typer.simulate(pause=False)
        with Center():
            yield typer

        yield SingleLineEngineSettingsContainer(
            classes="settings-group-container",
        )
        yield StandardEngineSettingsContainer(
            classes="settings-group-container",
        )
        yield ContentSettingsContainer(classes="settings-group-container")

    def watch__is_active(self) -> None:
        typer = self.query_one(TyperSimulator)
        if self._is_active:
            self.can_focus = False
            typer.resume()
        else:
            self.can_focus = True
            typer.pause()

    def on_focus(self) -> None:
        if self._is_active:
            return

        if self._last_focused:
            self._last_focused.focus()
        else:
            self.screen.focus_next()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        self._is_active = self.has_focus_within
        self._last_focused = event.control

    def on_descendant_blur(self) -> None:
        self._is_active = self.has_focus_within
