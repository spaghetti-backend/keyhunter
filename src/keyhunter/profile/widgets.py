from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import CenterMiddle, HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from .schemas import TypingSummary


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


class TypingSummaryView(Widget):
    typing_summary: reactive[TypingSummary | None] = reactive(None, recompose=True)

    def __init__(self, typing_summary: TypingSummary | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_reactive(TypingSummaryView.typing_summary, typing_summary)

    def compose(self) -> ComposeResult:
        if not self.typing_summary:
            yield Label("Your typing statistics will be shown here")
        else:
            accuracy = round(
                (self.typing_summary.correct_chars / self.typing_summary.total_chars)
                * 100,
                2,
            )
            hits = f"{self.typing_summary.correct_chars}/{self.typing_summary.total_chars} ({accuracy}%)"
            yield StatisticRow(label="Accuracy", data=hits, classes="statistic-row")

            yield StatisticRow(
                label="Elapsed time",
                data=(
                    datetime.min + timedelta(seconds=self.typing_summary.elapsed_time)
                ).strftime("%M:%S"),
                classes="statistic-row",
            )

            cpm = round(
                self.typing_summary.total_chars
                / (self.typing_summary.elapsed_time / 60)
            )
            speed = f"{cpm} cpm"
            yield StatisticRow(label="Speed", data=speed, classes="statistic-row")


class Profile(CenterMiddle):
    def compose(self) -> ComposeResult:
        yield TypingSummaryView(id="stat")

    async def update_last_typing_result(self, typing_summary: TypingSummary) -> None:
        self.query_one(TypingSummaryView).typing_summary = typing_summary
