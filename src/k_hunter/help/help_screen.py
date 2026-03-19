from textual.containers import VerticalScroll
from textual.widgets import Markdown
from textual.app import ComposeResult
from textual.screen import ModalScreen


class HelpScreen(ModalScreen[None]):
    BINDINGS = [("escape", "close_help", "Close")]
    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-screen-container {
        width: 60;
        height: 90%;
        align: center middle;
        scrollbar-size: 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-screen-container"):
            with open("src/k_hunter/help/help.md") as f:
                md = f.read()
            yield Markdown(md)

    def action_close_help(self):
        self.app.pop_screen()
