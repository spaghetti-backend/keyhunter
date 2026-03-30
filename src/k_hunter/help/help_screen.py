from typing import ClassVar
from textual.containers import VerticalScroll
from textual.widgets import Markdown
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import BindingType, Binding


class HelpContainer(VerticalScroll):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "scroll_down", show=False),
        Binding("k", "scroll_up", show=False),
    ]


class HelpScreen(ModalScreen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "close_help", "Close"),
    ]
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
    HELP = """
### Global

- **Ctrl + t** — switch to typing screen  
- **Ctrl + s** — switch to settings  
- **Ctrl + p** — switch to profile  

**Navigation:**

- **j / Tab / ↓** — next item  
- **k / Shift + Tab / ↑** — previous item  

---

### Settings

- **Ctrl + z** — undo changes  
- **Ctrl + d** — reset to default values  

- **PageDown / Ctrl + f** — next settings group  
- **PageUp / Ctrl + b** — previous settings group  

---

### Lists and dropdowns

- **Enter / Space / l** — open / close list  

> Navigation uses global keys ↑ / ↓ or j / k.

---

### Sliders and numeric values

- **h / ← / -** — decrease value  
- **l / → / + / =** — increase value  

---

💡 Main hotkeys are also displayed in the bottom panel.  
The footer can be hidden with **Ctrl + o**.
        """

    def compose(self) -> ComposeResult:
        with HelpContainer(id="help-screen-container"):
            yield Markdown(self.HELP)

    def action_close_help(self):
        self.app.pop_screen()
