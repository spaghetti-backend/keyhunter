from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.widgets import ContentSwitcher, ListView

from .app_settings import AppSettingsContainer
from .content_settings import ContentSettingsContainer
from .settings_sidebar import Sidebar
from .typer_settings import TyperSettingsContainer

if TYPE_CHECKING:
    from k_hunter.main import KeyHunter


class SettingsContainer(VerticalScroll, can_focus=False):
    app: "KeyHunter"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+d", "reset_to_default", "Default"),
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
        Binding("ctrl+f,pagedown", "page_down", "Next", priority=True, show=True),
        Binding("ctrl+b,pageup", "page_up", "Previous", priority=True, show=True),
    ]

    def compose(self) -> ComposeResult:
        with self.prevent(ListView.Highlighted):
            yield Sidebar(id="sidebar")
        with ContentSwitcher(
            id="settings-group-switcher", initial="app-settings-container"
        ):
            yield AppSettingsContainer(
                id="app-settings-container", classes="settings-group-container"
            )
            yield TyperSettingsContainer(
                id="typer-settings-container", classes="settings-group-container"
            )
            yield ContentSettingsContainer(
                id="content-settings-container", classes="settings-group-container"
            )

    def action_undo(self) -> None:
        self.app.settings_service.undo()
        self.refresh_bindings()

    def action_reset_to_default(self) -> None:
        self.app.settings_service.reset_to_default()
        self.refresh_bindings()

    def action_cursor_down(self) -> None:
        self.screen.focus_next()

    def action_cursor_up(self) -> None:
        self.screen.focus_previous()

    def action_page_down(self) -> None:
        self.query_one("#sidebar", Sidebar).action_cursor_down()

    def action_page_up(self) -> None:
        self.query_one("#sidebar", Sidebar).action_cursor_up()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "undo":
            return True if self.app.settings_service.has_updates else None
        else:
            return True

    # Sidebar
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            self.query_one(ContentSwitcher).current = event.item.id
            self.screen.focus_next()
