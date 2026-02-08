from typing import Callable

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from keyhunter.settings.schemas import SingleLineEngineSettings

from .base_engine import BaseEngine


class SingleLineEngine(BaseEngine):
    def __init__(self, settings: SingleLineEngineSettings) -> None:
        super().__init__(settings)

        self._enable_pre_content_space = settings.enable_pre_content_space
        self._pre_content_space = (
            (settings.width // 2) if settings.enable_pre_content_space else 0
        )

    @property
    def has_pre_content_space(self) -> bool:
        return self._enable_pre_content_space

    @has_pre_content_space.setter
    def has_pre_content_space(self, active: bool) -> None:
        self._enable_pre_content_space = active
        self.resize()

    @property
    def current_char(self) -> Segment:
        return self._chars[self._current_char_idx]

    @current_char.setter
    def current_char(self, current_char: Segment) -> None:
        self._chars[self._current_char_idx] = current_char

    @property
    def has_next(self) -> bool:
        return self._current_char_idx < (len(self._chars) - 1)

    def _update_current_char(self, style: Style) -> None:
        self.current_char = Segment(self.current_char.text, style)

    def _set_chars_style(self, get_char_style: Callable) -> None:
        self._chars = [
            Segment(
                text=char.text,
                style=get_char_style(self, char.style),
            )
            for char in self._chars
        ]

    def prepare_content(self, text: str) -> None:
        text = " ".join(text.split())

        before_chars = [
            Segment(" ", self.default_style) for _ in range(self._pre_content_space)
        ]

        self._chars = before_chars + [
            Segment(char, self.default_style) for char in text
        ]

        self._current_char_idx = self._pre_content_space
        self._update_current_char(self.next_char_style)

    def resize(self) -> None:
        if self.has_pre_content_space:
            before_center = self._width // 2
        else:
            before_center = 0

        if self._chars:
            before_chars = [
                Segment(" ", self.default_style) for _ in range(before_center)
            ]

            self._chars = (
                before_chars + self._chars[self._pre_content_space : len(self._chars)]
            )

        self._current_char_idx = (
            self._current_char_idx - self._pre_content_space + before_center
        )
        self._pre_content_space = before_center

    def build_placeholder(self, y: int, text: str) -> Strip:
        if y != 0:
            return Strip.blank(self._width)

        text = f"{text:^{self._width}}"

        return Strip([Segment(char, self.default_style) for char in text])

    def build_line(self, y: int) -> Strip:
        if not self._chars or y != 0:
            return Strip.blank(self._width)

        if self.has_pre_content_space:
            start = max(0, self._current_char_idx - self._pre_content_space)
        else:
            addition = self._width // 2
            if self._current_char_idx <= addition:
                start = 0
            else:
                start = max(0, self._current_char_idx - addition)
        end = min(start + self._width, len(self._chars))

        return Strip(self._chars[start:end])
