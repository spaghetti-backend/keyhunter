from typing import Callable

from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.strip import Strip

from keyhunter.settings.schemas import SingleLineEngineSettings

from .base_engine import BaseEngine


class SingleLineEngine(BaseEngine):

    def __init__(self, settings: SingleLineEngineSettings) -> None:
        super().__init__(settings)

        self.enable_pre_content_space = settings.enable_pre_content_space
        self._pre_content_space = (
            (settings.width // 2) if settings.enable_pre_content_space else 0
        )

    @property
    def _current_segment(self) -> Segment:
        return self._segments[self._current_segment_idx]

    @_current_segment.setter
    def _current_segment(self, current_segment: Segment) -> None:
        self._segments[self._current_segment_idx] = current_segment

    @property
    def total_chars(self) -> int:
        return len(self._segments) - self._pre_content_space

    @property
    def correct_chars(self) -> int:
        return sum(self._type_results)

    def _update_current_segment(self, style: Style) -> None:
        self._current_segment = Segment(self._current_segment.text, style)

    def _update_segments(self, type_result: bool) -> bool:
        if type_result:
            self._update_current_segment(self.matched_style)
        else:
            self._update_current_segment(self.mismatched_style)

        self._current_segment_idx += 1

        if self._current_segment_idx < len(self._segments):
            self._update_current_segment(self.next_char_style)
            return True
        else:
            return False

    def _set_segments_style(self, get_segment_style: Callable) -> None:
        self._segments = [
            Segment(
                text=segment.text,
                style=get_segment_style(self, segment.style),
            )
            for segment in self._segments
        ]

    def prepare_content(self, text: str) -> None:
        text = " ".join(text.split())
        self._type_results.clear()

        before_segments = [
            Segment(" ", self.default_style) for _ in range(self._pre_content_space)
        ]

        self._segments = before_segments + [
            Segment(char, self.default_style) for char in text
        ]

        self._current_segment_idx = self._pre_content_space
        self._update_current_segment(self.next_char_style)

    def resize(self) -> None:
        if self.enable_pre_content_space:
            before_center = self._width // 2
        else:
            before_center = 0

        if self._segments:
            before_segments = [
                Segment(" ", self.default_style) for _ in range(before_center)
            ]

            self._segments = (
                before_segments
                + self._segments[self._pre_content_space : len(self._segments)]
            )

        self._current_segment_idx = (
            self._current_segment_idx - self._pre_content_space + before_center
        )
        self._pre_content_space = before_center

    def process_key(self, key: events.Key) -> bool:
        type_result = self._current_segment.text == key.character
        self._type_results.append(type_result)

        return self._update_segments(type_result)

    def build_placeholder(self, y: int, text: str) -> Strip:
        if y != 0:
            return Strip.blank(self._width)

        text = f"{text:^{self._width}}"

        return Strip([Segment(char, self.default_style) for char in text])

    def build_line(self, y: int) -> Strip:
        if not self._segments or y != 0:
            return Strip.blank(self._width)

        if self.enable_pre_content_space:
            start = max(0, self._current_segment_idx - self._pre_content_space)
        else:
            addition = self._width // 2
            if self._current_segment_idx <= addition:
                start = 0
            else:
                start = max(0, self._current_segment_idx - addition)
        end = min(start + self._width, len(self._segments))

        return Strip(self._segments[start:end])
