from textual import on
from textual.app import App, ComposeResult
from textual.containers import CenterMiddle, Container, VerticalScroll
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, Footer

from keyhunter.settings import constants
from keyhunter.settings.schemas import AppSettings
from keyhunter.settings.service import SettingsService
from keyhunter.settings.widgets import Settings
from keyhunter.statistic.widgets import TypingStatistic
from keyhunter.typer.typer import Typer


class KeyHunter(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("t", "switch_widget('typer')", "Type H"),
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
        with ContentSwitcher(initial="typer-container"):
            yield CenterMiddle(
                Typer(settings=self.settings, id="typer"), id="typer-container"
            )
            yield VerticalScroll(
                Settings(id="settings"),
                id="settings-container",
                classes="settings",
            )
            with CenterMiddle(id="statistic-container"):
                yield TypingStatistic(id="statistic", classes="")
        yield Footer()

    def action_switch_widget(self, widget_name: str) -> None:
        switcher = self.query_one(ContentSwitcher)
        if switcher.current == "settings-container":
            self.query_one("#settings", Settings).is_active = False
        elif widget_name == "settings":
            self.query_one("#settings", Settings).is_active = True

        switcher.current = widget_name + "-container"
        widget = self.query_one(f"#{widget_name}")
        widget.focus()

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
