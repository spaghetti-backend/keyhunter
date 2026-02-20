from typing import ClassVar, Literal

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import HorizontalGroup
from textual.validation import Validator
from textual.widgets import Input, Label, Select, Switch
from textual.widgets._select import SelectOverlay

from keyhunter.settings.commands import SettingChangeCommand
from keyhunter.settings.messages import SettingChanged


class VimSelect(Select):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space,l", "show_overlay", "Show Overlay", show=False),
        Binding("up,k", "cursor_up", "Cursor Up", show=False),
        Binding("down,j", "cursor_down", "Cursor Down", show=False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type_to_search = False

    def action_cursor_up(self):
        if self.expanded:
            self.query_one(SelectOverlay).action_cursor_up()
        else:
            self.screen.focus_previous()

    def action_cursor_down(self):
        if self.expanded:
            self.query_one(SelectOverlay).action_cursor_down()
        else:
            self.screen.focus_next()


class SelectSetting(HorizontalGroup):
    def __init__(
        self,
        command: type[SettingChangeCommand],
        id: str,
        label: str,
        values: list[str],
        default: str | None = None,
        allow_blank: bool = False,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.command = command
        self.label = label
        self.values = values
        self.default = default
        self.allow_blank = allow_blank

    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="setting-label")
        with self.prevent(Select.Changed):
            yield VimSelect.from_values(
                values=self.values,
                allow_blank=self.allow_blank,
                value=self.default,
                classes="setting-select",
                compact=True,
            )

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()

        self.post_message(
            SettingChanged(
                command=self.command(event.value),
            )
        )


class InputSetting(HorizontalGroup):
    def __init__(
        self,
        command: type[SettingChangeCommand],
        id: str,
        label: str,
        default: str | int | float,
        validators: list[Validator],
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.command = command
        self.label = label
        self.default = default
        self.validators = validators
        self._current_value = str(default)

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="setting-label")
        with self.prevent(Input.Changed):
            yield Input(
                value=self._current_value,
                type=self._default_type(),
                validators=self.validators,
                select_on_focus=False,
                classes="setting-input",
                compact=True,
            )

    def _default_type(self) -> Literal["text", "integer", "number"]:
        match self.default:
            case str():
                return "text"
            case int():
                return "integer"
            case float():
                return "number"

    def _convert_to_default_type(self, value: str) -> str | int | float:
        match self.default:
            case str():
                return value
            case int():
                return int(value)
            case float():
                return float(value)

    def on_input_changed(self, message: Input.Changed) -> None:
        self.app.clear_notifications()
        if message.validation_result and not message.validation_result.is_valid:
            for failure in message.validation_result.failure_descriptions:
                self.notify(message=failure, title=self.label, severity="error")

    @on(Input.Submitted)
    @on(Input.Blurred)
    def process_input_submit(self, event: Input.Submitted | Input.Blurred) -> None:
        event.stop()
        new_value = event.value

        if new_value == self._current_value:
            return

        if event.validation_result and event.validation_result.is_valid:
            self.post_message(
                SettingChanged(
                    command=self.command(self._convert_to_default_type(new_value)),
                )
            )
            self._current_value = new_value


class SwitchSetting(HorizontalGroup):
    def __init__(
        self,
        command: type[SettingChangeCommand],
        id: str,
        label: str,
        default: bool,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.command = command
        self.label = label
        self.default = default

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="setting-label")
        yield Switch(
            value=self.default,
            classes="setting-switch height-auto",
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        self.post_message(
            SettingChanged(
                command=self.command(event.value),
            )
        )
