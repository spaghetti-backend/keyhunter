from time import perf_counter
from typing import TYPE_CHECKING, Sequence

from textual import events, on
from textual.app import ComposeResult
from textual.containers import CenterMiddle
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from keyhunter.content.schemas import ContentType, Language
from keyhunter.content.service import ContentService
from keyhunter.settings.schemas import (
    AppSettingsState,
    TyperBorder,
    TyperEngine,
)

from .schemas import Keystroke
from .single_line_engine import SingleLineEngine
from .standard_engine import StandardEngine

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter

BORDER_SIZE: int = 2
MILLISECONDS_MULTIPLIER = 1000


class Typer(Widget, can_focus=True):
    app: "KeyHunter"

    class TypingCompleted(Message):
        def __init__(self, typing_summary: Sequence[Keystroke]) -> None:
            super().__init__()
            self.typing_summary = tuple(typing_summary)

    class TypingStarted(Message): ...

    def __init__(self, settings: AppSettingsState, **kwargs):
        super().__init__(**kwargs)

        self.content_service = ContentService(settings.content)
        self._is_active_session = False
        self._session_start_time_ms = 0
        self._keystroke_start_time_ms = 0
        self._keystrokes = []
        self.styles.border = (settings.typer.border, self.styles.base.color)

        self._set_engine(settings)

    @property
    def _timer_ms(self) -> int:
        return round(perf_counter() * MILLISECONDS_MULTIPLIER)

    def _set_engine(self, settings: AppSettingsState) -> None:
        match settings.typer.engine:
            case TyperEngine.STANDARD:
                engine_settings = settings.typer.standard_engine
                self.engine = StandardEngine(engine_settings)
            case TyperEngine.SINGLE_LINE:
                engine_settings = settings.typer.single_line_engine
                self.engine = SingleLineEngine(engine_settings)

        self.engine.set_theme(self.app.available_themes[settings.theme])

        self.styles.height = engine_settings.height + BORDER_SIZE
        self.styles.width = engine_settings.width + BORDER_SIZE

    def on_mount(self) -> None:
        self._subscribe()

    def _subscribe(self) -> None:
        state = self.app.state
        self.watch(state, "_theme", self._on_theme_changed, init=False)
        self.watch(state.typer, "_engine", self._on_engine_changed, init=False)
        self.watch(state.typer, "_border", self._on_border_changed, init=False)

        sle_state = state.typer.single_line_engine
        self.watch(sle_state, "_width", self._on_sle_width_changed, init=False)
        self.watch(
            sle_state,
            "_start_from_center",
            self._on_sle_start_from_center_changed,
            init=False,
        )

        se_state = state.typer.standard_engine
        self.watch(se_state, "_width", self._on_se_width_changed, init=False)
        self.watch(se_state, "_height", self._on_se_height_changed, init=False)

        self.watch(
            state.content, "_language", self._on_content_language_changed, init=False
        )
        self.watch(
            state.content, "_content_type", self._on_content_type_changed, init=False
        )
        self.watch(
            state.content,
            "_content_lenght",
            self._on_content_lenght_changed,
            init=False,
        )

    def _on_theme_changed(self, theme: str) -> None:
        self.engine.set_theme(self.app.available_themes[theme])

    def _on_border_changed(self, border: TyperBorder) -> None:
        self.styles.border = (border, self.styles.base.color)

    def _on_engine_changed(self) -> None:
        self._set_engine(self.app.state)

    def _on_sle_start_from_center_changed(self, start_from_center: bool) -> None:
        if isinstance(self.engine, SingleLineEngine):
            self.engine.start_from_center = start_from_center

    def _on_sle_width_changed(self, width: int) -> None:
        if isinstance(self.engine, SingleLineEngine):
            self.engine.width = width
            self.styles.width = width + BORDER_SIZE

    def _on_se_width_changed(self, width: int) -> None:
        if isinstance(self.engine, StandardEngine):
            self.engine.width = width
            self.styles.width = width + BORDER_SIZE

    def _on_se_height_changed(self, height: int) -> None:
        if isinstance(self.engine, StandardEngine):
            self.engine.height = height
            self.styles.height = height + BORDER_SIZE

    def _on_content_language_changed(self, content_language: Language) -> None:
        self.content_service.language = content_language

    def _on_content_type_changed(self, content_type: ContentType) -> None:
        self.content_service.content_type = content_type

    def _on_content_lenght_changed(self, content_lenght: int) -> None:
        self.content_service.content_lenght = content_lenght

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
            self.engine.prepare_content(self.content_service.generate())
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

        if self._keystrokes:
            self.post_message(self.TypingCompleted(typing_summary=self._keystrokes))

    def render_line(self, y: int) -> Strip:
        if not self._is_active_session:
            return self.engine.build_placeholder(y, self.content_service.placeholder)

        return self.engine.build_line(y)


class TyperContainer(CenterMiddle, can_focus=True):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield Typer(settings=self.app.state)

    @on(events.Focus)
    def handle_focus(self) -> None:
        self.query_one(Typer).focus()
