from textual.app import App, ComposeResult
from textual.widgets import ContentSwitcher, Footer

from keyhunter import const as CONST
from keyhunter.profile.service import ProfileService
from keyhunter.profile.widgets import Profile
from keyhunter.settings.messages import SettingChanged
from keyhunter.settings.schemas import AppSettings
from keyhunter.settings.service import SettingsService
from keyhunter.settings.widgets.settings_container import SettingsContainer
from keyhunter.typer.widgets import Typer, TyperContainer


class KeyHunter(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("t", "switch_widget('typer')", "Typing"),
        ("s", "switch_widget('settings')", "Settings"),
        ("p", "switch_widget('profile')", "Profile"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.profile_service = ProfileService()
        self.settings = AppSettings()
        self.settings_service = SettingsService(self.settings)

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="typer"):
            yield TyperContainer(id="typer")
            yield Profile(id="profile")
            yield SettingsContainer(id="settings")

        yield Footer(show_command_palette=False)

    def action_switch_widget(self, widget_name: str) -> None:
        switcher = self.query_one(ContentSwitcher)

        switcher.current = widget_name

        self.screen.focus_next()

    def on_mount(self) -> None:
        self.watch(self.settings, CONST.THEME_KEY, self._on_theme_changed)

    def _on_theme_changed(self, theme: str) -> None:
        self.theme = theme

    def on_setting_changed(self, event: SettingChanged) -> None:
        self.settings_service.update(event.command)

    async def on_typer_typing_completed(self, event: Typer.TypingCompleted) -> None:
        await self.query_one(Profile).update_last_typing_result(event.typing_summary)
        self.action_switch_widget("profile")


def main():
    app = KeyHunter()
    app.run()


if __name__ == "__main__":
    main()
