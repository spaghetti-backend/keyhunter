from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets._footer import Footer, FooterKey


class HelpFooter(Horizontal):
    def compose(self) -> ComposeResult:
        with Horizontal(id="footer"):
            yield Footer(show_command_palette=False)

        with Horizontal(id="static-keybindings"):
            yield FooterKey("ctrl+t", "^t", "Typing", "switch_widget('typer')")
            yield FooterKey("ctrl+s", "^s", "Settings", "switch_widget('settings')")
            yield FooterKey("ctrl+p", "^p", "Profile", "switch_widget('profile')")
            yield FooterKey("f1", "F1", "Help", "show_help")
