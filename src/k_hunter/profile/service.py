from datetime import datetime, timedelta
from typing import Sequence

from k_hunter import const as CONST
from k_hunter.typer.schemas import Keystroke

from .schemas import ProfileData, TypingSessionSummary, TypingSummary
from .storage import SQLite3Storage


class ProfileService:

    def __init__(self, profile_data: ProfileData) -> None:
        self._storage = SQLite3Storage()
        self._profile_data = profile_data
        self._profile_data.last_session = self._load_last_session_summary()
        self._profile_data.today_sessions = self._load_sessions_summary(today_only=True)
        self._profile_data.all_time_sessions = self._load_sessions_summary(
            today_only=False
        )

    def _load_last_session_summary(self) -> TypingSessionSummary:
        try:
            speed, accuracy, elapsed_time_ms = self._storage.load_last_session_summary()
            return TypingSessionSummary(
                speed=self._as_cpm(speed),
                accuracy=self._as_percent(accuracy),
                time=self._convert_time(elapsed_time_ms),
            )
        except TypeError:
            return TypingSessionSummary()

    def _load_sessions_summary(self, today_only: bool) -> TypingSummary:
        try:
            (
                sessions_count,
                speed_avg,
                speed_max,
                accuracy_avg,
                accuracy_max,
                sessions_time_ms,
            ) = self._storage.load_sessions_summary(today_only=today_only)

            return TypingSummary(
                time=self._convert_time(sessions_time_ms),
                typing_sessions=str(sessions_count),
                speed_avg=self._as_cpm(speed_avg),
                speed_max=self._as_cpm(speed_max),
                accuracy_avg=self._as_percent(accuracy_avg),
                accuracy_max=self._as_percent(accuracy_max),
            )
        except TypeError:
            return TypingSummary()

    def add(self, typing_summary: Sequence[Keystroke]) -> None:
        if not typing_summary:
            return

        keystrokes = sorted(typing_summary, key=lambda x: x.key)
        keystrokes_summary = []
        session_summary = {
            CONST.TOTAL_CHARS_KEY: 0,
            CONST.CORRECT_CHARS_KEY: 0,
            CONST.ELAPSED_TIME_MS_KEY: 0,
        }

        last_char = keystrokes[0].key
        char_summary = {
            CONST.CHAR_KEY: last_char,
            CONST.TOTAL_KEY: 0,
            CONST.CORRECT_KEY: 0,
            CONST.ELAPSED_TIME_MS_KEY: 0,
        }

        for keystroke in keystrokes:
            if keystroke.key != last_char:
                keystrokes_summary.append(char_summary)
                last_char = keystroke.key
                char_summary = {
                    CONST.CHAR_KEY: last_char,
                    CONST.TOTAL_KEY: 0,
                    CONST.CORRECT_KEY: 0,
                    CONST.ELAPSED_TIME_MS_KEY: 0,
                }

            char_summary[CONST.TOTAL_KEY] += 1
            char_summary[CONST.CORRECT_KEY] += keystroke.is_matched
            char_summary[CONST.ELAPSED_TIME_MS_KEY] += keystroke.elapsed_time_ms
        else:
            if char_summary[CONST.TOTAL_KEY] > 0:
                keystrokes_summary.append(char_summary)

        for summary in keystrokes_summary:
            total_chars = summary[CONST.TOTAL_KEY]
            correct_chars = summary[CONST.CORRECT_KEY]
            elapsed_time_ms = summary[CONST.ELAPSED_TIME_MS_KEY]

            summary[CONST.ACCURACY_KEY] = self._compute_typing_accuracy(
                total_chars, correct_chars
            )
            summary[CONST.SPEED_KEY] = self._compute_typing_speed(
                total_chars, elapsed_time_ms
            )

            session_summary[CONST.TOTAL_CHARS_KEY] += total_chars
            session_summary[CONST.CORRECT_CHARS_KEY] += correct_chars
            session_summary[CONST.ELAPSED_TIME_MS_KEY] += elapsed_time_ms

        session_total_chars = session_summary[CONST.TOTAL_CHARS_KEY]
        session_correct_chars = session_summary[CONST.CORRECT_CHARS_KEY]
        session_elapsed_time_ms = session_summary[CONST.ELAPSED_TIME_MS_KEY]
        session_accuracy = self._compute_typing_accuracy(
            total_chars=session_total_chars,
            correct_chars=session_correct_chars,
        )
        session_speed = self._compute_typing_speed(
            total_chars=session_summary[CONST.TOTAL_CHARS_KEY],
            elapsed_time_ms=session_summary[CONST.ELAPSED_TIME_MS_KEY],
        )

        session_summary[CONST.ACCURACY_KEY] = session_accuracy
        session_summary[CONST.SPEED_KEY] = session_speed

        self._storage.add_session_summary(session_summary, keystrokes_summary)

        self._profile_data.last_session = TypingSessionSummary(
            speed=self._as_cpm(session_speed),
            accuracy=self._as_percent(session_accuracy),
            time=self._convert_time(session_elapsed_time_ms),
        )

        self._profile_data.today_sessions = self._load_sessions_summary(today_only=True)
        self._profile_data.all_time_sessions = self._load_sessions_summary(
            today_only=False
        )

    def _convert_time(self, elapsed_time_ms: int) -> str:
        dt = datetime.min
        delta = timedelta(milliseconds=elapsed_time_ms)
        format = "%d days %H:%M:%S" if delta.days else "%H:%M:%S"
        return (dt + delta).strftime(format)

    def _as_cpm(self, speed: int) -> str:
        return f"{speed / CONST.FLOAT_TO_INT_SCALE_2DP}cpm"

    def _as_percent(self, accuracy: int) -> str:
        return f"{accuracy / CONST.FLOAT_TO_INT_SCALE_2DP}%"

    def _compute_typing_accuracy(self, total_chars: int, correct_chars: int) -> int:
        accuracy = round((correct_chars / total_chars) * CONST.PERCENT_SCALE_2DP)
        return int(accuracy)

    def _compute_typing_speed(self, total_chars: int, elapsed_time_ms: int) -> int:
        minutes = elapsed_time_ms / (60 * CONST.MILLISECONDS_MULTIPLIER)
        cpm = round((total_chars / minutes) * 100)
        return int(cpm)
