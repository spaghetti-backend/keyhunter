from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView


class Sidebar(ListView, can_focus=False):
    def compose(self) -> ComposeResult:
        yield ListItem(
            Label("App", classes="sidebar-item"), id="app-settings-container"
        )
        yield ListItem(
            Label("Typing", classes="sidebar-item"), id="typer-settings-container"
        )
        yield ListItem(
            Label("Content", classes="sidebar-item"), id="content-settings-container"
        )
