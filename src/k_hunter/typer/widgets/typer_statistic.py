from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label

from k_hunter.profile.schemas import TypingSessionSummary

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class TypingStatistic(HorizontalGroup):
    app: "KeyHunter"
    last_session: reactive[TypingSessionSummary] = reactive(
        TypingSessionSummary(), recompose=True
    )

    def compose(self) -> ComposeResult:
        yield Label(f"Speed: {self.last_session.speed}")
        yield Label(f"Accuracy: {self.last_session.accuracy}")

    def on_mount(self) -> None:
        self.watch(self.app.profile_data, "last_session", self._update)

    def _update(self, last_session: TypingSessionSummary) -> None:
        self.last_session = last_session
