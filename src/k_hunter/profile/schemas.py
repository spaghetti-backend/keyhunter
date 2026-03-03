from typing import NamedTuple

from textual.dom import DOMNode
from textual.reactive import reactive


class TypingSessionSummary(NamedTuple):
    speed: str = "N/A"
    accuracy: str = "N/A"
    time: str = "00:00"


class TypingSummary(NamedTuple):
    time: str = "00:00:00"
    typing_sessions: str = "0"
    speed_avg: str = "N/A"
    speed_max: str = "N/A"
    accuracy_avg: str = "N/A"
    accuracy_max: str = "N/A"


class ProfileData(DOMNode):
    last_session: reactive[TypingSessionSummary] = reactive(
        TypingSessionSummary, init=False
    )
    today_sessions: reactive[TypingSummary] = reactive(TypingSummary, init=False)
    all_time_sessions: reactive[TypingSummary] = reactive(TypingSummary, init=False)
