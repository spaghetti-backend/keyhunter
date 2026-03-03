from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import CenterMiddle

from .typer import Typer


if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class TyperContainer(CenterMiddle):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield Typer(settings=self.app.settings)
