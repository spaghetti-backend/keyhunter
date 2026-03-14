from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Select

from k_hunter import const as CONST

from .components import SelectSetting

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


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
                id="theme",
                label="Theme",
                values=available_themes,
                default=current_theme,
                target=self.app.settings,
                attr_name=CONST.THEME_KEY,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings, CONST.THEME_KEY, self._on_theme_changed, init=False
        )

    def _on_theme_changed(self, theme: str) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = theme


class AppSettingsContainer(VerticalScroll, can_focus=False):
    BORDER_TITLE = "App"

    def compose(self) -> ComposeResult:
        yield ThemeSelector(classes="setting-container")
