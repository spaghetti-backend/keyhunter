from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll

from keyhunter.settings.schemas import AppSettingsState
from keyhunter.settings.simulator import TyperSimulator
from keyhunter.settings.widgets.app_settings import AppSettingsContainer
from keyhunter.settings.widgets.content_settings import ContentSettingsContainer
from keyhunter.settings.widgets.typer_settings import (
    SingleLineEngineSettingsContainer,
    StandardEngineSettingsContainer,
    TyperSettingsContainer,
)


class SettingsContainer(VerticalScroll):
    def __init__(self, settings: AppSettingsState, *args, **kwargs) -> None:
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
