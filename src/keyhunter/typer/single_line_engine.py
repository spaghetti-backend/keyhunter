from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.strip import Strip
from textual.theme import Theme

from keyhunter.settings.schemas import SingleLineEngineSettings


class SingleLineEngine:
    matched_style = Style.parse("green")
    mismatched_style = Style.parse("red")
    default_style = Style.parse("white")
    next_char_style = default_style + Style(underline=True)

    def __init__(self, settings: SingleLineEngineSettings) -> None:
        self._segments = []
        self._type_results = []
        self._current_segment_idx = 0
        self.enable_pre_content_space: bool = settings.enable_pre_content_space
        self._width = settings.width
        self._height = settings.height

        self._pre_content_space = (
            (settings.width // 2) if settings.enable_pre_content_space else 0
        )
        self._settings = settings

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int) -> None:
        if new_width > self._settings.max_width:
            self._width = self._settings.max_width
        elif new_width < self._settings.min_width:
            self._width = self._settings.min_width
        else:
            self._width = new_width

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int) -> None:
        if new_height > self._settings.max_height:
            self._height = self._settings.max_height
        elif new_height < self._settings.min_height:
            self._height = self._settings.min_height
        else:
            self._height = new_height

    @property
    def _current_segment(self) -> Segment:
        return self._segments[self._current_segment_idx]

    @_current_segment.setter
    def _current_segment(self, current_segment: Segment) -> None:
        self._segments[self._current_segment_idx] = current_segment

    @property
    def total_chars(self):
        return len(self._segments) - self._pre_content_space

    @property
    def correct_chars(self):
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

    def set_chars_style(self, theme: Theme) -> None:
        def segment_style(self, style: Style | None) -> Style:
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

        self._segments = [
            Segment(
                text=segment.text,
                style=segment_style(self, segment.style),
            )
            for segment in self._segments
        ]

        self.default_style = default_style
        self.matched_style = matched_style
        self.mismatched_style = mismatched_style
        self.next_char_style = next_char_style

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
        if self._settings.enable_pre_content_space:
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

        if self._settings.enable_pre_content_space:
            start = max(0, self._current_segment_idx - self._pre_content_space)
        else:
            addition = self._width // 2
            if self._current_segment_idx <= addition:
                start = 0
            else:
                start = max(0, self._current_segment_idx - addition)
        end = min(start + self._width, len(self._segments))

        return Strip(self._segments[start:end])
