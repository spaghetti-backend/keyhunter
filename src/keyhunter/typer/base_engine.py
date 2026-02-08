from abc import ABC, abstractmethod
from typing import Callable

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.theme import Theme


class BaseEngine(ABC):
    matched_style = Style.parse("green")
    mismatched_style = Style.parse("red")
    default_style = Style.parse("white")
    next_char_style = default_style + Style(underline=True)

    def __init__(self, settings) -> None:
        self._chars = []
        self._current_char_idx = 0

        self._width = settings.width
        self._min_width = settings._min_width
        self._max_width = settings._max_width

        self._height = settings.height
        self._min_height = settings._min_height
        self._max_height = settings._max_height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int) -> None:
        if new_width == self._width:
            return

        if new_width > self._max_width:
            self._width = self._max_width
        elif new_width < self._min_width:
            self._width = self._min_width
        else:
            self._width = new_width

        self.resize()

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int) -> None:
        if new_height == self.height:
            return

        if new_height > self._max_height:
            self._height = self._max_height
        elif new_height < self._min_height:
            self._height = self._min_height
        else:
            self._height = new_height

        self.resize()

    @property
    @abstractmethod
    def current_char(self) -> Segment | None: ...

    @property
    def has_next(self) -> bool: ...

    @abstractmethod
    def _set_chars_style(self, get_char_style: Callable) -> None: ...

    @abstractmethod
    def _update_current_char(self, style: Style) -> None: ...

    def mark_current_char(self, is_matched: bool) -> None:
        if is_matched:
            self._update_current_char(self.matched_style)
        else:
            self._update_current_char(self.mismatched_style)

    def next(self) -> None:
        self._current_char_idx += 1
        self._update_current_char(self.next_char_style)

    def set_theme(self, theme: Theme) -> None:
        def get_char_style(self, style: Style | None) -> Style:
            match style:
                case self.matched_style:
                    return matched_style
                case self.mismatched_style:
                    return mismatched_style
                case self.next_char_style:
                    return next_char_style
                case _:
                    return default_style

        bgcolor = theme.background if theme.background else "#111111"
        default_style = Style(color=theme.foreground, bgcolor=bgcolor)
        matched_style = Style(color=theme.success, bgcolor=bgcolor)
        mismatched_style = Style(color=theme.error, bgcolor=bgcolor)
        next_char_style = default_style + Style(underline=True)

        self._set_chars_style(get_char_style)

        self.default_style = default_style
        self.matched_style = matched_style
        self.mismatched_style = mismatched_style
        self.next_char_style = next_char_style

    @abstractmethod
    def prepare_content(self, text: str) -> None: ...

    @abstractmethod
    def resize(self) -> None: ...

    @abstractmethod
    def build_placeholder(self, y: int, text: str) -> Strip: ...

    @abstractmethod
    def build_line(self, y: int) -> Strip: ...
