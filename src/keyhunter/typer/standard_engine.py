from typing import Callable

from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.strip import Strip

from keyhunter.typer.base_engine import BaseEngine


class StandardEngine(BaseEngine):
    _text = ""

    @property
    def _current_segment(self) -> Segment | None:
        segments_count = 0
        for line in self._segments:
            if self._current_segment_idx >= (len(line) + segments_count):
                segments_count += len(line)
            else:
                return line[self._current_segment_idx - segments_count]

    @_current_segment.setter
    def _current_segment(self, current_segment: Segment) -> None:
        segments_count = 0
        for line in self._segments:
            if self._current_segment_idx >= (len(line) + segments_count):
                segments_count += len(line)
            else:
                line[self._current_segment_idx - segments_count] = current_segment
                return

    @property
    def _current_line(self) -> int | None:
        segments_count = 0
        for line_index, line in enumerate(self._segments):
            if self._current_segment_idx >= (len(line) + segments_count):
                segments_count += len(line)
            else:
                return line_index

    @property
    def total_chars(self) -> int:
        return sum(len(line) for line in self._segments)

    @property
    def correct_chars(self) -> int:
        return sum(self._type_results)

    def _update_current_segment(self, style: Style) -> None:
        if current_segment := self._current_segment:
            self._current_segment = Segment(current_segment.text, style)

    def _update_segments(self, type_result: bool) -> bool:
        if type_result:
            self._update_current_segment(self.matched_style)
        else:
            self._update_current_segment(self.mismatched_style)

        self._current_segment_idx += 1

        if self._current_segment_idx < self.total_chars:
            self._update_current_segment(self.next_char_style)
            return True
        else:
            return False

    def _set_segments_style(self, get_segment_style: Callable) -> None:
        self._segments = [
            [
                Segment(segment.text, get_segment_style(self, segment.style))
                for segment in line
            ]
            for line in self._segments
        ]

    def _segmentize_word(self, word: str, append_space: bool = True) -> list[Segment]:
        segments = [Segment(char, self.default_style) for char in word]
        if append_space:
            segments.append(Segment(" ", self.default_style))

        return segments

    def prepare_content(self, text: str) -> None:
        self._type_results.clear()
        self._text = text
        self.resize()

    def resize(self) -> None:
        self._segments.clear()
        words = self._text.split()
        line = self._segmentize_word(words[0])
        for word in words[1:]:
            if (len(line) + len(word)) < self._width:
                line.extend(self._segmentize_word(word))
            else:
                self._segments.append(line)
                line = self._segmentize_word(word)
        if line:
            self._segments.append(line)

        self._segments[-1].pop()

        self._current_segment_idx = 0
        self._update_current_segment(self.next_char_style)

    def process_key(self, key: events.Key) -> bool:
        if current_segment := self._current_segment:
            type_result = current_segment.text == key.character
        else:
            return False

        self._type_results.append(type_result)

        return self._update_segments(type_result)

    def _blank_strip(self) -> Strip:
        return Strip([Segment(" ", self.default_style) for _ in range(self._width)])

    def build_placeholder(self, y: int, text: str) -> Strip:
        if y != self._height // 2:
            return self._blank_strip()

        text = f"{text:^{self._width}}"

        return Strip([Segment(char, self.default_style) for char in text])

    def build_line(self, y: int) -> Strip:
        if not self._segments or y >= self._height:
            return Strip.blank(self._width)

        middle = self._height // 2
        if self._current_line is not None and self._current_line > middle:
            y += self._current_line - middle

        if y > len(self._segments) - 1:
            return self._blank_strip()

        return Strip(self._segments[y])
