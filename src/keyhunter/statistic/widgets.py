from datetime import datetime

from textual.app import ComposeResult
from textual.containers import CenterMiddle, HorizontalGroup
from textual.screen import ModalScreen
from textual.widgets import Footer, Label

from keyhunter.typer.typer import Typer


class StatisticRow(HorizontalGroup):
    def __init__(
        self, label: str, data: str, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.label = label
        self.data = data

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="statistic-label")
        yield Label(content=self.data, classes="statistic-data")


class TypingStatistic(ModalScreen[tuple[int, str]]):
    BINDINGS = [
        ("r", "return('retry')", "Retry"),
        ("q", "return('quit')", "Quit"),
    ]

    def __init__(
        self,
        statistic: Typer.Statistic,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._statistic = statistic

    def compose(self) -> ComposeResult:
        with CenterMiddle():
            hits_percentage = round(
                (self._statistic.correct / self._statistic.total) * 100, 2
            )
            hits_data = f"{self._statistic.correct}/{self._statistic.total} ({hits_percentage}%)"
            yield StatisticRow(label="Hits", data=hits_data, classes="statistic-row")

            yield StatisticRow(
                label="Elapsed",
                data=(datetime.min + self._statistic.elapsed).strftime("%M:%S.%f")[:-4],
                classes="statistic-row",
            )

            cpm_data = str(
                round(
                    self._statistic.total
                    / (self._statistic.elapsed.total_seconds() / 60),
                    2,
                )
            )
            yield StatisticRow(
                label="Chars per minute", data=cpm_data, classes="statistic-row"
            )

        yield Footer(show_command_palette=False)

    def action_return(self, action: str) -> None:
        if action == "retry":
            self.dismiss((0, "retry"))
        elif action == "quit":
            self.dismiss((1, "quit"))
