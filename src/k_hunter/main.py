from typing import ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import ContentSwitcher

from k_hunter import const as CONST
from k_hunter.content.service import ContentService
from k_hunter.help import HelpFooter, HelpScreen
from k_hunter.profile.schemas import ProfileData
from k_hunter.profile.service import ProfileService
from k_hunter.profile.widgets import Profile
from k_hunter.settings.messages import SettingChanged
from k_hunter.settings.schemas import AppSettings
from k_hunter.settings.service import SettingsService
from k_hunter.settings.widgets.settings_container import SettingsContainer
from k_hunter.typer.widgets import Typer, TyperContainer


class KeyHunter(App):
    CSS_PATH = "style.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("f1", "show_help", "Help", show=False),
        Binding("ctrl+t", "switch_widget('typer')", "Typing", show=False),
        Binding("ctrl+s", "switch_widget('settings')", "Settings", show=False),
        Binding(
            "ctrl+p", "switch_widget('profile')", "Profile", priority=True, show=False
        ),
        Binding("ctrl+o", "toggle_footer", "Toggle footer", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.profile_data = ProfileData()
        self.profile_service = ProfileService(self.profile_data)
        self.settings = AppSettings()
        self.settings_service = SettingsService(self.settings)
        self.content_service = ContentService(self.settings.content)

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="typer"):
            yield TyperContainer(id="typer")
            yield Profile(id="profile")
            yield SettingsContainer(id="settings")

        yield HelpFooter()

    def action_switch_widget(self, widget_name: str) -> None:
        self.query_one(ContentSwitcher).current = widget_name

        self.screen.focus_next()

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_toggle_footer(self) -> None:
        help_footer = self.query_one(HelpFooter)
        help_footer.visible = not help_footer.visible

    def on_mount(self) -> None:
        self.watch(self.settings, CONST.THEME_KEY, self._on_theme_changed)

    def _on_theme_changed(self, theme: str) -> None:
        self.theme = theme

    def on_setting_changed(self, event: SettingChanged) -> None:
        self.settings_service.update(event.command)

    @work(thread=True)
    def on_typer_typing_completed(self, event: Typer.TypingCompleted) -> None:
        self.profile_service.add(event.typing_summary)


def main():
    app = KeyHunter()
    app.run()


if __name__ == "__main__":
    main()
