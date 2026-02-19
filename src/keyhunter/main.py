from textual import on
from textual.app import App, ComposeResult
from textual.widgets import ContentSwitcher, Footer

from keyhunter.profile.service import ProfileService
from keyhunter.profile.widgets import Profile
from keyhunter.settings.messages import SettingStateChanged
from keyhunter.settings.schemas import AppSettingsState
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
        self.state = AppSettingsState()

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="typer"):
            yield TyperContainer(id="typer")
            yield Profile(id="profile")
            yield SettingsContainer(settings=self.state, id="settings")

        yield Footer(show_command_palette=False)

    def action_switch_widget(self, widget_name: str) -> None:
        switcher = self.query_one(ContentSwitcher)

        switcher.current = widget_name
        self.query_one(f"#{widget_name}").focus()

    def on_mount(self) -> None:
        self.watch(self.state, "_theme", self._on_theme_changed)

    def _on_theme_changed(self, theme: str) -> None:
        self.theme = theme

    @on(SettingStateChanged)
    def on_setting_changed(self, m):
        self.state.update(m.command)

    @on(Typer.TypingCompleted)
    async def update_typing_statistic(self, message: Typer.TypingCompleted) -> None:
        await self.query_one(Profile).update_last_typing_result(message.typing_summary)
        self.action_switch_widget("profile")


def main():
    app = KeyHunter()
    app.run()


if __name__ == "__main__":
    main()
