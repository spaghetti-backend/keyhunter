from datetime import datetime
from typing import TYPE_CHECKING

from textual import events
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from keyhunter.content.service import ContentService, ContentType
from keyhunter.settings.schemas import (
    AppSettings,
    TyperEngine,
)

from .single_line_engine import SingleLineEngine
from .standard_engine import StandardEngine

if TYPE_CHECKING:
    from datetime import timedelta

BORDER_SIZE: int = 2


class Typer(Widget, can_focus=True):

    class Statistic(Message):
        def __init__(self, elapsed: "timedelta", total: int, correct: int) -> None:
            self.elapsed = elapsed
            self.total = total
            self.correct = correct
            super().__init__()

    def __init__(self, settings: AppSettings, **kwargs):
        super().__init__(**kwargs)

        self.content_manager = ContentService()
        self.is_active_session: bool = False
        self.styles.border = (settings.typer.border, self.styles.base.color)

        self._set_engine(settings)

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
        self.engine.set_chars_style(self.app.available_themes[settings.theme])

    def on_mount(self, event: events.Mount) -> None:
        self.watch(self.app, "settings", self.on_settings_change, init=True)
        self.engine.set_chars_style(self.app.available_themes[self.app.theme])
        return super()._on_mount(event)

    def on_settings_change(
        self, old_settings: AppSettings, new_settings: AppSettings
    ) -> None:
        if old_settings.theme != new_settings.theme:
            self.engine.set_chars_style(self.app.available_themes[new_settings.theme])

        if old_settings.typer != new_settings.typer:
            self._set_engine(new_settings)

    def on_key(self, event: events.Key) -> None:
        if self.is_active_session:
            if event.key == "escape":
                self.stop_typing()
            else:
                has_next = self.engine.process_key(event)

                if not has_next:
                    self.stop_typing()
        elif event.key == "space":
            self.engine.prepare_content(
                self.content_manager.generate(ContentType.WORDS, 100)
            )
            self.start_typing()
        else:
            return None

        event.stop()
        self.refresh()

    def start_typing(self) -> None:
        self.is_active_session = True
        self._start_time = datetime.now()

    def stop_typing(self) -> None:
        self.post_message(
            self.Statistic(
                datetime.now() - self._start_time,
                self.engine.total_chars,
                self.engine.correct_chars,
            )
        )

        self.is_active_session = False

    def retry(self) -> None:
        pass

    def render_line(self, y: int) -> Strip:
        if not self.is_active_session:
            return self.engine.build_placeholder(y, self.content_manager.placeholder)

        return self.engine.build_line(y)
