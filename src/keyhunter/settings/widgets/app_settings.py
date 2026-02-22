from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Select

from keyhunter import const as CONST
from keyhunter.settings.commands import SetThemeCommand

from .components import SelectSetting

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class ThemeSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        current_theme = self.app.settings.theme
        available_themes = [
            theme_name
            for theme_name, theme in self.app.available_themes.items()
            if theme.dark and theme.name != "textual-ansi"
        ]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetThemeCommand,
                id="theme",
                label="Theme",
                values=available_themes,
                default=current_theme,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings, CONST.THEME_KEY, self._on_theme_changed, init=False
        )

    def _on_theme_changed(self, theme: str) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = theme


class AppSettingsContainer(VerticalGroup):
    BORDER_TITLE = "App"

    def compose(self) -> ComposeResult:
        yield ThemeSelector(classes="setting-container")
