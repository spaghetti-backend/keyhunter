from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Select

from keyhunter.settings.commands import SetThemeCommand

from .components import SelectSetting

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class ThemeSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_theme = self.app.settings.theme
        available_themes = [
            theme for theme in self.app.available_themes if theme != "textual-ansi"
        ]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetThemeCommand,
                id="theme",
                label="Theme",
                values=available_themes,
                default=current_theme,
            )


class AppSettingsContainer(VerticalGroup):
    BORDER_TITLE = "App"

    def compose(self) -> ComposeResult:
        yield ThemeSelector(classes="setting-container")
