from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, Footer

from keyhunter.settings import constants
from keyhunter.settings.schemas import AppSettings
from keyhunter.settings.service import SettingsService
from keyhunter.settings.widgets import Settings
from keyhunter.statistic.widgets import TypingStatistic
from keyhunter.typer.typer import Typer, TyperContainer


class KeyHunter(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("t", "switch_widget('typer')", "Typing"),
        ("s", "switch_widget('settings')", "Settings"),
        ("p", "switch_widget('statistic')", "Profile"),
    ]

    settings: reactive[AppSettings] = reactive(AppSettings, init=False)

    def __init__(self) -> None:
        super().__init__()
        self.settings_manager = SettingsService()
        self.set_reactive(KeyHunter.settings, self.settings_manager.settings)
        self.theme = self.settings.theme

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="typer"):
            yield TyperContainer(id="typer")
            yield Settings(id="settings")
            yield TypingStatistic(id="statistic")

        yield Footer(show_command_palette=False)

    def action_switch_widget(self, widget_name: str) -> None:
        switcher = self.query_one(ContentSwitcher)

        switcher.current = widget_name
        self.query_one(f"#{widget_name}").focus()

    def watch_settings(self, settings: AppSettings) -> None:
        setting = settings.last_modified
        if setting and setting.name == constants.THEME:
            self.theme = setting.value

    @on(Settings.Update)
    def update_settings(self, message: Settings.Update) -> None:
        message.stop()
        self.settings = self.settings_manager.update(message.setting)

    @on(Settings.Save)
    def save_settings(self, message: Settings.Save) -> None:
        message.stop()
        self.settings_manager.save()

    @on(Typer.Statistic)
    async def show_typing_statistic(self, message: Typer.Statistic) -> None:
        await self.query_one(TypingStatistic).update_last_typing_result(message)
        self.action_switch_widget("statistic")


def main():
    app = KeyHunter()
    app.run()


if __name__ == "__main__":
    main()
