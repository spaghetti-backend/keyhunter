from datetime import datetime

from textual.app import ComposeResult
from textual.containers import CenterMiddle, HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

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


class Stat(Widget):
    statistic: reactive[Typer.Statistic | None] = reactive(None, recompose=True)

    def __init__(self, statistic: Typer.Statistic | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_reactive(Stat.statistic, statistic)

    def compose(self) -> ComposeResult:
        with CenterMiddle():
            if not self.statistic:
                yield Label("There is no any typing result")
            else:
                hits_percentage = round(
                    (self.statistic.correct / self.statistic.total) * 100, 2
                )
                hits_data = f"{self.statistic.correct}/{self.statistic.total} ({hits_percentage}%)"
                yield StatisticRow(
                    label="Hits", data=hits_data, classes="statistic-row"
                )

                yield StatisticRow(
                    label="Elapsed",
                    data=(datetime.min + self.statistic.elapsed).strftime("%M:%S.%f")[
                        :-4
                    ],
                    classes="statistic-row",
                )

                cpm_data = str(
                    round(
                        self.statistic.total
                        / (self.statistic.elapsed.total_seconds() / 60),
                        2,
                    )
                )
                yield StatisticRow(
                    label="Chars per minute", data=cpm_data, classes="statistic-row"
                )


class TypingStatistic(Widget):
    def compose(self) -> ComposeResult:
        yield Stat(id="stat")
        yield Label("Statistic")

    async def update_last_typing_result(self, statistic: Typer.Statistic) -> None:
        self.query_one(Stat).statistic = statistic
