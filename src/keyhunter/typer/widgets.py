from time import perf_counter
from typing import TYPE_CHECKING

from textual import events, on
from textual.app import ComposeResult
from textual.containers import CenterMiddle
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from keyhunter.content.service import ContentService
from keyhunter.profile.schemas import Keystroke, TypingSessionSummary
from keyhunter.settings import constants
from keyhunter.settings.schemas import (
    AppSettings,
    TyperEngine,
)

from .single_line_engine import SingleLineEngine
from .standard_engine import StandardEngine

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter

BORDER_SIZE: int = 2
MILLISECONDS_MULTIPLIER = 1000


class Typer(Widget, can_focus=True):

    class TypingCompleted(Message):
        def __init__(self, typing_summary: TypingSessionSummary) -> None:
            super().__init__()
            self.typing_summary = typing_summary

    class TypingStarted(Message): ...

    def __init__(self, settings: AppSettings, **kwargs):
        super().__init__(**kwargs)

        self.content_service = ContentService(settings.content)
        self._is_active_session = False
        self._session_start_time_ms = 0
        self._keystroke_time_ms = 0
        self._keystrokes = []
        self.styles.border = (settings.typer.border, self.styles.base.color)

        self._set_engine(settings)

    @property
    def _timer_ms(self) -> int:
        return round(perf_counter() * MILLISECONDS_MULTIPLIER)

    def _set_engine(self, settings: AppSettings) -> None:
        match settings.typer.typer_engine:
            case TyperEngine.STANDARD:
                engine_settings = settings.typer.standard_engine
                self.engine = StandardEngine(engine_settings)
            case TyperEngine.SINGLE_LINE:
                engine_settings = settings.typer.single_line_engine
                self.engine = SingleLineEngine(engine_settings)

        self.engine.set_theme(self.app.available_themes[settings.theme])

        self.styles.height = engine_settings.height + BORDER_SIZE
        self.styles.width = engine_settings.width + BORDER_SIZE

    def on_mount(self, event: events.Mount) -> None:
        self.watch(self.app, "settings", self.on_settings_change, init=True)
        self.engine.set_theme(self.app.available_themes[self.app.theme])
        return super()._on_mount(event)

    def on_settings_change(self, settings: AppSettings) -> None:
        setting = settings.last_modified
        if not setting:
            return

        match setting.name:
            case constants.THEME:
                self.engine.set_theme(self.app.available_themes[setting.value])
            case constants.TYPER_BORDER:
                self.styles.border = (setting.value, self.styles.base.color)
            case constants.TYPER_ENGINE:
                self._set_engine(settings)
            case constants.SLE_PRE_CONTENT_SPACE:
                if settings.typer.typer_engine == TyperEngine.SINGLE_LINE:
                    self.engine.has_pre_content_space = setting.value  # type: ignore
            case constants.SLE_WIDTH | constants.SE_WIDTH:
                width = int(setting.value)
                self.engine.width = width
                self.styles.width = width + BORDER_SIZE
            case constants.SE_HEIGHT:
                height = int(setting.value)
                self.engine.height = height
                self.styles.height = height + BORDER_SIZE
            case constants.CONTENT_TYPE:
                self.content_service.content_type = setting.value
            case constants.CONTENT_LENGHT:
                self.content_service.content_lenght = int(setting.value)

    def _process_keystroke(self, event: events.Key) -> None:
        if current_char := self.engine.current_char:
            current_time = self._timer_ms
            keystroke_elapsed_time_ms = current_time - self._keystroke_time_ms
            is_matched = current_char.text == event.character
            self._keystrokes.append(
                Keystroke(
                    key=current_char.text,
                    is_matched=is_matched,
                    elapsed_time_ms=keystroke_elapsed_time_ms,
                )
            )
            self._keystroke_time_ms = current_time
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
        self.refresh()

    def start_typing(self) -> None:
        self._keystrokes.clear()
        self._is_active_session = True
        self._session_start_time_ms = self._timer_ms
        self._keystroke_time_ms = self._session_start_time_ms
        self.post_message(self.TypingStarted())

    def stop_typing(self) -> None:
        self._is_active_session = False

        if not self._keystrokes:
            return

        elapsed_time_ms = self._timer_ms - self._session_start_time_ms
        typing_summary = TypingSessionSummary(
            elapsed_time_ms=elapsed_time_ms,
            total_chars=len(self._keystrokes),
            correct_chars=sum([keystroke.is_matched for keystroke in self._keystrokes]),
            keystrokes=self._keystrokes,
        )
        self.post_message(self.TypingCompleted(typing_summary=typing_summary))
        print(self._session_start_time_ms)
        print(self._timer_ms)
        print(typing_summary)

    def render_line(self, y: int) -> Strip:
        if not self._is_active_session:
            return self.engine.build_placeholder(y, self.content_service.placeholder)

        return self.engine.build_line(y)


class TyperContainer(CenterMiddle, can_focus=True):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield Typer(settings=self.app.settings)

    @on(events.Focus)
    def handle_focus(self, _) -> None:
        self.query_one(Typer).focus()
