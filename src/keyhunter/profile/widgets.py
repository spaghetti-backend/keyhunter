from typing import Sequence

from textual import events
from textual.app import ComposeResult
from textual.containers import (
    Center,
    CenterMiddle,
    Container,
    HorizontalGroup,
)
from textual.reactive import reactive
from textual.widgets import Label, Rule

from keyhunter.typer.schemas import Keystroke

from .schemas import TypingSessionSummary, TypingSummary
from .service import ProfileService


class StatItem(Container):
    def __init__(self, label: str, value: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value

    def compose(self) -> ComposeResult:
        with Center():
            yield Label(content=self._label, classes="statistic-label")
        with Center():
            yield Label(content=self._value, classes="statistic-value")


class LastTypingSession(HorizontalGroup):
    typing_summary: reactive[TypingSessionSummary] = reactive(
        TypingSessionSummary(), recompose=True
    )
    BORDER_TITLE = "Last typing session"

    def compose(self) -> ComposeResult:
        yield StatItem("Accuracy", self.typing_summary.accuracy)
        yield StatItem("Speed", self.typing_summary.speed)


class TypingSessions(Container):
    typing_summary: reactive[TypingSummary] = reactive(TypingSummary(), recompose=True)

    def compose(self) -> ComposeResult:
        with Container(classes="stat-group width-auto height-auto horizontal"):
            yield StatItem("Time", self.typing_summary.time)
            yield StatItem("Typing sessions", self.typing_summary.typing_sessions)
        with Container(classes="stat-group width-auto height-auto horizontal"):
            yield StatItem("Top speed", self.typing_summary.speed_max)
            yield StatItem("Average speed", self.typing_summary.speed_avg)
        with Container(classes="stat-group width-auto height-auto horizontal"):
            yield StatItem("Top accuracy", self.typing_summary.accuracy_max)
            yield StatItem("Average accuracy", self.typing_summary.accuracy_avg)

    def on_resize(self, event: events.Resize):
        if event.container_size.width < 120:
            class_to_remove = "horizontal"
            class_to_add = "vertical"
        else:
            class_to_remove = "vertical"
            class_to_add = "horizontal"

        for container in self.query(".stat-group"):
            container.remove_class(class_to_remove)
            container.add_class(class_to_add)


class Profile(CenterMiddle):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profile_service = ProfileService()

    def compose(self) -> ComposeResult:
        with Center():
            yield LastTypingSession(id="last_session")
        yield Rule(line_style="none")
        with Center():
            today_sessions = TypingSessions(id="today_sessions")
            today_sessions.border_title = "Statistics for today"
            yield today_sessions
        yield Rule(line_style="none")
        with Center():
            all_time_sessions = TypingSessions(id="all_time_sessions")
            all_time_sessions.border_title = "All time statistics"
            yield all_time_sessions

    def on_mount(self) -> None:
        self._update_statistic_widgets()

    def _update_statistic_widgets(self) -> None:
        self.query_one("#last_session", LastTypingSession).typing_summary = (
            self._profile_service.last_session
        )
        self.query_one("#today_sessions", TypingSessions).typing_summary = (
            self._profile_service.today
        )
        self.query_one("#all_time_sessions", TypingSessions).typing_summary = (
            self._profile_service.all_time
        )

    async def update_last_typing_result(
        self, typing_summary: Sequence[Keystroke]
    ) -> None:
        self._profile_service.add(typing_summary)
        self._update_statistic_widgets()
