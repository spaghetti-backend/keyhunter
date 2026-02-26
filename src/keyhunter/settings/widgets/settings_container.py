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
    from keyhunter.main import KeyHunter


class SettingsContainer(VerticalScroll, can_focus=False):
    app: "KeyHunter"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+r", "restore", "Restore"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+d", "reset_to_default", "Default"),
    ]

    def compose(self) -> ComposeResult:
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

    def action_restore(self) -> None:
        self.app.settings_service.restore()
        self.refresh_bindings()

    def action_save(self) -> None:
        self.app.settings_service.save()
        self.refresh_bindings()

    def action_reset_to_default(self) -> None:
        self.app.settings_service.reset_to_default()
        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action in ("undo", "restore"):
            return True if self.app.settings_service.has_updates else None
        elif action == "save":
            return True if not self.app.settings_service.saved else None
        else:
            return True

    # Sidebar
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            self.query_one(ContentSwitcher).current = event.item.id

    def on_setting_changed(self) -> None:
        self.refresh_bindings()
