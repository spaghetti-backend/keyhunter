from datetime import datetime
from typing import TYPE_CHECKING

from textual import events, on
from textual.app import ComposeResult
from textual.containers import CenterMiddle
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from keyhunter.content.service import ContentService
from keyhunter.settings import constants
from keyhunter.settings.schemas import (
    AppSettings,
    TyperEngine,
)

from .single_line_engine import SingleLineEngine
from .standard_engine import StandardEngine

if TYPE_CHECKING:
    from datetime import timedelta
    from keyhunter.main import KeyHunter

BORDER_SIZE: int = 2


class TyperContainer(CenterMiddle, can_focus=True):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield Typer(settings=self.app.settings)

    @on(events.Focus)
    def handle_focus(self, _) -> None:
        self.query_one(Typer).focus()


class Typer(Widget, can_focus=True):

    class Statistic(Message):
        def __init__(self, elapsed: "timedelta", total: int, correct: int) -> None:
            self.elapsed = elapsed
            self.total = total
            self.correct = correct
            super().__init__()

    def __init__(self, settings: AppSettings, **kwargs):
        super().__init__(**kwargs)

        self.content_service = ContentService(settings.content)
        self.is_active_session: bool = False
        self.styles.border = (settings.typer.border, self.styles.base.color)

        self._set_engine(settings)
        self.engine.set_theme(self.app.available_themes[settings.theme])

    def _set_engine(self, settings: AppSettings) -> None:
        match settings.typer.typer_engine:
            case TyperEngine.STANDARD:
                engine_settings = settings.typer.standard_engine
                self.engine = StandardEngine(engine_settings)
            case TyperEngine.SINGLE_LINE:
                engine_settings = settings.typer.single_line_engine
                self.engine = SingleLineEngine(engine_settings)

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
                    self.engine.enable_pre_content_space = setting.value  # type: ignore
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

    def on_key(self, event: events.Key) -> None:
        if self.is_active_session:
            if event.key == "escape":
                self.stop_typing()
            else:
                has_next = self.engine.process_key(event)

                if not has_next:
                    self.stop_typing()
        elif event.key == "space":
            self.engine.prepare_content(self.content_service.generate())
            self.start_typing()
        else:
            return None

        event.stop()
        self.refresh()

    def start_typing(self) -> None:
        self.is_active_session = True
        self._start_time = datetime.now()

    def stop_typing(self) -> None:
        self.is_active_session = False

        if not self.engine.typed_chars:
            return

        self.post_message(
            self.Statistic(
                datetime.now() - self._start_time,
                self.engine.typed_chars,
                self.engine.correct_chars,
            )
        )

    def render_line(self, y: int) -> Strip:
        if not self.is_active_session:
            return self.engine.build_placeholder(y, self.content_service.placeholder)

        return self.engine.build_line(y)
