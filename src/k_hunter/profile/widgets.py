from typing import TYPE_CHECKING

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

from .schemas import TypingSessionSummary, TypingSummary

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


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
    last_session: reactive[TypingSessionSummary] = reactive(
        TypingSessionSummary(), recompose=True
    )
    BORDER_TITLE = "Last typing session"

    def compose(self) -> ComposeResult:
        yield StatItem("Speed", self.last_session.speed)
        yield StatItem("Accuracy", self.last_session.accuracy)


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
    app: "KeyHunter"

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
        self.watch(
            self.app.profile_data,
            "last_session",
            self._refresh_typing_summary,
        )

    def _refresh_typing_summary(self) -> None:
        self.query_one("#last_session", LastTypingSession).last_session = (
            self.app.profile_data.last_session
        )

        self.query_one("#today_sessions", TypingSessions).typing_summary = (
            self.app.profile_data.today_sessions
        )
        self.query_one("#all_time_sessions", TypingSessions).typing_summary = (
            self.app.profile_data.all_time_sessions
        )
