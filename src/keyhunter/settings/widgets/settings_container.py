from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import ContentSwitcher, ListView

from keyhunter.settings.widgets.app_settings import AppSettingsContainer
from keyhunter.settings.widgets.content_settings import ContentSettingsContainer
from keyhunter.settings.widgets.settings_sidebar import Sidebar
from keyhunter.settings.widgets.typer_settings import TyperSettingsContainer


class SettingsContainer(VerticalScroll, can_focus=False):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")
        with ContentSwitcher(
            id="settings-group-switcher", initial="app-settings-container"
        ):
            yield AppSettingsContainer(
                id="app-settings-container", classes="settings-group-container"
            )
            yield TyperSettingsContainer(
                id="typer-settings-container", classes="settings-group-container"
            )
            yield ContentSettingsContainer(
                id="content-settings-container", classes="settings-group-container"
            )

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            self.query_one(ContentSwitcher).current = event.item.id
