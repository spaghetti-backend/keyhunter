from textual import on
from textual.app import App, ComposeResult
from textual.containers import CenterMiddle, VerticalScroll
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, Footer

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
                Settings(id="settings"), id="settings-container", classes="settings"
            )
        yield Footer()

    def action_switch_widget(self, widget: str) -> None:
        switcher = self.query_one(ContentSwitcher)
        if switcher.current == "settings-container":
            self.query_one("#settings", Settings).is_active = False
        elif widget == "settings":
            self.query_one("#settings", Settings).is_active = True

        switcher.current = widget + "-container"
        typer = self.query_one(f"#{widget}")
        typer.focus()

    def watch_settings(self, old, new) -> None:
        if old.theme != new.theme:
            self.theme = new.theme

    @on(Settings.Update)
    def update_settings(self, message: Settings.Update) -> None:
        message.stop()
        self.settings = self.settings_manager.update(message.data)

    @on(Settings.Save)
    def save_settings(self, message: Settings.Save) -> None:
        message.stop()
        self.settings_manager.save()

    @on(Typer.Statistic)
    def show_typing_statistic(self, message: Typer.Statistic) -> None:
        def process_statistic_action(action: tuple[int, str] | None) -> None:
            if not action or action[0] == 1:
                self.exit()

            self.query_one("#typer", Typer).retry()

        self.push_screen(TypingStatistic(message), process_statistic_action)


def main():
    app = KeyHunter()
    app.run()
    # app.run(inline=True)


if __name__ == "__main__":
    main()
