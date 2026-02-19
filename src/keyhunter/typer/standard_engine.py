from typing import Callable

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from keyhunter.typer.base_engine import BaseEngine


class StandardEngine(BaseEngine):
    _text = ""
    _lines = []

    @property
    def current_char(self) -> Segment | None:
        chars_count = 0
        for line in self._lines:
            if self._current_char_idx >= (len(line) + chars_count):
                chars_count += len(line)
            else:
                return line[self._current_char_idx - chars_count]

    @current_char.setter
    def current_char(self, current_char: Segment) -> None:
        chars_count = 0
        for line in self._lines:
            if self._current_char_idx >= (len(line) + chars_count):
                chars_count += len(line)
            else:
                line[self._current_char_idx - chars_count] = current_char
                return

    @property
    def has_next(self) -> bool:
        return self._current_char_idx < (sum([len(line) for line in self._lines]) - 1)

    @property
    def _current_line(self) -> int | None:
        chars_count = 0
        for line_index, line in enumerate(self._lines):
            if self._current_char_idx >= (len(line) + chars_count):
                chars_count += len(line)
            else:
                return line_index

    @property
    def _total_chars(self) -> int:
        return sum(len(line) for line in self._lines)

    def _update_current_char(self, style: Style) -> None:
        if current_char := self.current_char:
            self.current_char = Segment(current_char.text, style)

    def _set_chars_style(self, get_char_style: Callable) -> None:
        self._lines = [
            [Segment(char.text, get_char_style(self, char.style)) for char in line]
            for line in self._lines
        ]

    def _segmentize_word(self, word: str) -> list[Segment]:
        segments = [Segment(char, self.default_style) for char in word]
        segments.append(Segment(" ", self.default_style))

        return segments

    def _make_lines(self, words, f=lambda x: x) -> None:
        line = f(words[0])
        for word in words[1:]:
            if (len(line) + len(word)) < self._width:
                line.extend(f(word))
            else:
                self._lines.append(line)
                line = f(word)
        if line:
            self._lines.append(line)

    def prepare_content(self, text: str) -> None:
        self._text = text

        self._lines.clear()

        words = self._text.split()

        self._make_lines(words, self._segmentize_word)

        self._lines[-1].pop()

        self._current_char_idx = 0
        self._update_current_char(self.next_char_style)

    def resize(self) -> None:
        if not self._lines:
            return

        segmentized_text = []
        [segmentized_text.extend(line) for line in self._lines]

        self._lines.clear()

        words = []
        word_with_space = []
        for char in segmentized_text:
            word_with_space.append(char)
            if char.text == " ":
                words.append(word_with_space)
                word_with_space = []

        words.append(word_with_space)

        self._make_lines(words)

    def _blank_strip(self) -> Strip:
        return Strip([Segment(" ", self.default_style) for _ in range(self._width)])

    def build_placeholder(self, y: int, text: str) -> Strip:
        if y != self._height // 2:
            return self._blank_strip()

        text = f"{text:^{self._width}}"

        return Strip([Segment(char, self.default_style) for char in text])

    def build_line(self, y: int) -> Strip:
        if not self._lines or y >= self._height:
            return Strip.blank(self._width)

        middle = self._height // 2
        if self._current_line is not None and self._current_line > middle:
            y += self._current_line - middle

        if y > len(self._lines) - 1:
            return self._blank_strip()

        return Strip(self._lines[y])
