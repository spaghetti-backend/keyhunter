from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, Grid
from textual.reactive import reactive

from .typer import Typer
from .typer_hints_label import TyperHints
from .typer_statistic import TypingStatistic

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class TyperContainer(Grid):
    app: "KeyHunter"
    is_active_session: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Center():
            yield TypingStatistic().data_bind(TyperContainer.is_active_session)
        with Center():
            yield Typer(settings=self.app.settings)
        with Center():
            yield TyperHints().data_bind(TyperContainer.is_active_session)

    def on_typer_typing_started(self) -> None:
        self.is_active_session = True

    def on_typer_typing_completed(self) -> None:
        self.is_active_session = False
