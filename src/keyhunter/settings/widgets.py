from typing import Any, Literal

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Center, HorizontalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Number, Validator
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Rule, Select, Switch

from keyhunter.settings.simulator import TyperSimulator
from keyhunter.typer.typer import Typer

from .messages import InvalidSetting, SettingChanged
from .schemas import TyperEngine
from .service import AppSettings


class SelectSetting(HorizontalGroup):
    def __init__(
        self,
        name: str,
        id: str,
        label: str,
        values: list[str],
        default: str | None = None,
        allow_blank: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes="setting-row")
        self.label = label
        self.values = values
        self.default = default
        self.allow_blank = allow_blank
        self._init = False

    def compose(self) -> ComposeResult:
        yield Label(self.label, id=f"setting-{self.id}", classes="setting-label")
        yield Select.from_values(
            values=self.values,
            allow_blank=self.allow_blank,
            value=self.default,
            id=f"setting-select-{self.id}",
            classes="setting-select",
            compact=True,
        )

    @on(Select.Changed)
    def process_select_change(self, message: Select.Changed) -> None:
        message.stop()
        if not self._init:
            self._init = True
            return

        self.post_message(
            SettingChanged(
                name=self.name,  # type: ignore
                value=str(message.value),
            )
        )


class InputSetting(HorizontalGroup):
    def __init__(
        self,
        name: str,
        id: str,
        label: str,
        default: str | int | float,
        validators: list[Validator],
    ) -> None:
        super().__init__(name=name, id=id, classes="setting-row")
        self.label = label
        self.default = default
        self.validators = validators
        self._current = str(default)

    def compose(self) -> ComposeResult:
        yield Label(
            content=self.label, id=f"setting-{self.id}", classes="setting-label"
        )
        yield Input(
            value=str(self.default),
            type=self._default_type(),
            validators=self.validators,
            select_on_focus=False,
            id=f"setting-input-{self.id}",
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

    @on(Input.Changed)
    def process_input_change(self, message: Input.Changed) -> None:
        self.app.clear_notifications()
        if message.validation_result and not message.validation_result.is_valid:
            for failure in message.validation_result.failure_descriptions:
                self.notify(message=failure, title=self.label, severity="error")

    @on(Input.Submitted)
    @on(Input.Blurred)
    def process_input_submit(self, message: Input.Submitted | Input.Blurred) -> None:
        message.stop()
        if message.validation_result and message.validation_result.is_valid:
            if message.value == self._current:
                return
            self._current = message.value
            self.post_message(
                SettingChanged(
                    self.name,  # type: ignore
                    message.value,
                )
            )
        else:
            self.post_message(InvalidSetting(self.name))  # type: ignore


class SwitchSetting(HorizontalGroup):
    def __init__(
        self,
        name: str,
        id: str,
        label: str,
        default: bool,
    ) -> None:
        super().__init__(name=name, id=id, classes="setting-row")
        self.label = label
        self.default = default

    def compose(self) -> ComposeResult:
        yield Label(
            content=self.label, id=f"setting-{self.id}", classes="setting-label"
        )
        yield Switch(
            value=self.default,
            id=f"setting-switch-{self.id}",
            classes="setting-switch height-auto",
        )

    @on(Switch.Changed)
    def handle_switch_changed(self, message: Switch.Changed) -> None:
        message.stop()
        self.post_message(
            SettingChanged(
                self.name,  # type: ignore
                message.value,
            )
        )


class Settings(Widget):
    class Save(Message):
        def __init__(self, data: dict[str, Any]) -> None:
            super().__init__()
            self.data = data

    class Update(Message):
        def __init__(self, data: tuple[str, Any]) -> None:
            super().__init__()
            self.data = data

    data: dict[str, Any] = dict()
    invalid_settings: reactive[set] = reactive(set)
    is_active: reactive[bool] = reactive(False)

    def watch_invalid_settings(self):
        save_button = self.query_one("#save", Button)
        if self.invalid_settings:
            save_button.disabled = True
        else:
            save_button.disabled = False

    def watch_is_active(self):
        typer_simulator = self.query_one("#setting-typer", TyperSimulator)
        if self.is_active:
            typer_simulator.resume()
        else:
            typer_simulator.pause()

    def compose(self) -> ComposeResult:
        settings: AppSettings = self.app.settings  # type: ignore

        themes = [
            theme for theme in self.app.available_themes if theme != "textual-ansi"
        ]
        theme = self.app.theme
        with Center():
            yield SelectSetting(
                name="theme",
                id="theme-setting",
                label="Theme",
                values=themes,
                default=theme,
            )
        yield Rule(line_style="none")

        typer_settings = settings.typer
        values = [engine.value for engine in TyperEngine]
        with Center():
            yield SelectSetting(
                name="typer.typer_engine",
                id="typer-setting",
                label="Typer",
                values=values,
                default=typer_settings.typer_engine.value,
            )
        yield Rule(line_style="none")
        typer = TyperSimulator(
            settings=settings.typer, id="setting-typer", classes="setting-typer"
        )
        typer.can_focus = False
        typer.simulate()
        with Center():
            yield typer

        yield Rule(line_style="none")
        sle_settings = typer_settings.single_line_engine
        with Center():
            yield SwitchSetting(
                name="typer.single_line_engine.enable_pre_content_space",
                id="sle-pre-content-space",
                label="Pre content space",
                default=sle_settings.enable_pre_content_space,
            )
        yield Rule(line_style="none")

        sle_width_validator = Number(
            minimum=sle_settings.min_width, maximum=sle_settings.max_width
        )
        with Center():
            yield InputSetting(
                name="typer.single_line_engine.width",
                id="sle-width",
                label="Width",
                default=sle_settings.width,
                validators=[sle_width_validator],
            )
        yield Rule(line_style="none")

        yield Button(label="save", id="save")

    @on(SettingChanged)
    def update_settings(self, message: SettingChanged) -> None:
        message.stop()

        setting = message.name
        if setting in self.invalid_settings:
            self.invalid_settings.remove(setting)
            self.mutate_reactive(Settings.invalid_settings)

        self.post_message(self.Update((setting, message.value)))

    @on(InvalidSetting)
    def update_invalid_settings(self, message: InvalidSetting) -> None:
        message.stop()
        self.invalid_settings.add(message.name)
        self.mutate_reactive(Settings.invalid_settings)

    @on(Button.Pressed, "#save")
    def save_settings(self, message: Button.Pressed) -> None:
        message.stop()
        self.post_message(self.Save(self.data))
