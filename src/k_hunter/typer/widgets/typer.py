from time import perf_counter
from typing import TYPE_CHECKING, Sequence

from textual import events
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from k_hunter import const as CONST
from k_hunter.settings.schemas import (
    AppSettings,
    TyperBorder,
    TyperEngine,
)

from k_hunter.typer.schemas import Keystroke
from k_hunter.typer.engines.single_line_engine import SingleLineEngine
from k_hunter.typer.engines.standard_engine import StandardEngine

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class Typer(Widget, can_focus=True):
    app: "KeyHunter"

    class TypingCompleted(Message):
        def __init__(self, typing_summary: Sequence[Keystroke]) -> None:
            super().__init__()
            self.typing_summary = tuple(typing_summary)

    class TypingStarted(Message): ...

    def __init__(self, settings: AppSettings, **kwargs):
        super().__init__(**kwargs)

        self._is_active_session = False
        self._session_start_time_ms = 0
        self._keystroke_start_time_ms = 0
        self._keystrokes = []

        self._set_engine(settings)

    @property
    def _timer_ms(self) -> int:
        return round(perf_counter() * CONST.MILLISECONDS_MULTIPLIER)

    def _set_engine(self, settings: AppSettings) -> None:
        match settings.typer.engine:
            case TyperEngine.STANDARD:
                engine_settings = settings.typer.standard_engine
                self.engine = StandardEngine(engine_settings)
            case TyperEngine.SINGLE_LINE:
                engine_settings = settings.typer.single_line_engine
                self.engine = SingleLineEngine(engine_settings)

        self.engine.set_theme(self.app.available_themes[settings.theme])

        self.styles.height = engine_settings.height + CONST.BORDER_EXPANSION
        self.styles.width = engine_settings.width + CONST.BORDER_EXPANSION

    def on_mount(self) -> None:
        self._subscribe()
        self.engine.prepare_content(self.app.content_service.generate())

    def _subscribe(self) -> None:
        settings = self.app.settings
        self.watch(settings, CONST.THEME_KEY, self._on_theme_changed, init=False)
        self.watch(
            settings.typer, CONST.ENGINE_KEY, self._on_engine_changed, init=False
        )
        self.watch(settings.typer, CONST.BORDER_KEY, self._on_border_changed)

        sle_settings = settings.typer.single_line_engine
        self.watch(
            sle_settings, CONST.WIDTH_KEY, self._on_sle_width_changed, init=False
        )
        self.watch(
            sle_settings,
            CONST.SLE_START_FROM_CENTER_KEY,
            self._on_sle_start_from_center_changed,
            init=False,
        )

        se_settings = settings.typer.standard_engine
        self.watch(se_settings, CONST.WIDTH_KEY, self._on_se_width_changed, init=False)
        self.watch(
            se_settings, CONST.HEIGHT_KEY, self._on_se_height_changed, init=False
        )

    def _on_theme_changed(self, theme: str) -> None:
        self.engine.set_theme(self.app.available_themes[theme])

    def _on_border_changed(self, border: TyperBorder) -> None:
        self.styles.border = (border.value, self.styles.base.border_title_color)

    def _on_engine_changed(self) -> None:
        self._set_engine(self.app.settings)

    def _on_sle_start_from_center_changed(self, start_from_center: bool) -> None:
        if isinstance(self.engine, SingleLineEngine):
            self.engine.start_from_center = start_from_center

    def _on_sle_width_changed(self, width: int) -> None:
        if isinstance(self.engine, SingleLineEngine):
            self.engine.width = width
            self.styles.width = width + CONST.BORDER_EXPANSION

    def _on_se_width_changed(self, width: int) -> None:
        if isinstance(self.engine, StandardEngine):
            self.engine.width = width
            self.styles.width = width + CONST.BORDER_EXPANSION

    def _on_se_height_changed(self, height: int) -> None:
        if isinstance(self.engine, StandardEngine):
            self.engine.height = height
            self.styles.height = height + CONST.BORDER_EXPANSION

    def _process_keystroke(self, event: events.Key) -> None:
        if current_char := self.engine.current_char:
            current_time = self._timer_ms
            keystroke_elapsed_time_ms = current_time - self._keystroke_start_time_ms
            is_matched = current_char.text == event.character
            self._keystrokes.append(
                Keystroke(
                    key=current_char.text,
                    is_matched=is_matched,
                    elapsed_time_ms=keystroke_elapsed_time_ms,
                )
            )
            self._keystroke_start_time_ms = current_time
            self.engine.mark_current_char(is_matched)

            if self.engine.has_next:
                self.engine.next()
            else:
                self.stop_typing()

    def on_key(self, event: events.Key) -> None:
        if self._is_active_session:
            if event.key == "escape":
                self.stop_typing()
            else:
                self._process_keystroke(event)
        elif event.key == "space":
            self.start_typing()
        else:
            return None

        event.stop()
        event.prevent_default()
        self.refresh()

    def start_typing(self) -> None:
        self._keystrokes.clear()
        self._is_active_session = True
        self._session_start_time_ms = self._timer_ms
        self._keystroke_start_time_ms = self._session_start_time_ms
        self.post_message(self.TypingStarted())

    def stop_typing(self) -> None:
        self._is_active_session = False

        self.post_message(self.TypingCompleted(typing_summary=self._keystrokes))
        self.engine.prepare_content(self.app.content_service.generate())

    def render_line(self, y: int) -> Strip:
        return self.engine.build_line(y)
