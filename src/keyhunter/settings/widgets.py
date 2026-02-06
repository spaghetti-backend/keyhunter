from typing import TYPE_CHECKING, Literal

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Center, Container, HorizontalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Number, Validator
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Rule, Select, Switch

from keyhunter.content.schemas import ContentType
from keyhunter.settings import constants

from .messages import InvalidSetting, SettingChanged
from .schemas import SettingUpdateInfo, TyperBorder, TyperEngine
from .service import AppSettings
from .simulator import TyperSimulator

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class SelectSetting(HorizontalGroup):
    def __init__(
        self,
        id: str,
        label: str,
        values: list[str],
        default: str | None = None,
        allow_blank: bool = False,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.values = values
        self.default = default
        self.allow_blank = allow_blank
        self._init = False

    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="setting-label")
        yield Select.from_values(
            values=self.values,
            allow_blank=self.allow_blank,
            value=self.default,
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
                name=self.id,  # type: ignore
                value=str(message.value),
            )
        )


class InputSetting(HorizontalGroup):
    def __init__(
        self,
        id: str,
        label: str,
        default: str | int | float,
        validators: list[Validator],
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.default = default
        self.validators = validators
        self._current = str(default)

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="setting-label")
        yield Input(
            value=str(self.default),
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
                    self.id,  # type: ignore
                    message.value,
                )
            )
        else:
            self.post_message(InvalidSetting(self.id))  # type: ignore


class SwitchSetting(HorizontalGroup):
    def __init__(
        self,
        id: str,
        label: str,
        default: bool,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.default = default

    def compose(self) -> ComposeResult:
        yield Label(content=self.label, classes="setting-label")
        yield Switch(
            value=self.default,
            classes="setting-switch height-auto",
        )

    @on(Switch.Changed)
    def handle_switch_changed(self, message: Switch.Changed) -> None:
        message.stop()
        self.post_message(
            SettingChanged(
                self.id,  # type: ignore
                message.value,
            )
        )


class Settings(VerticalScroll, can_focus=True):
    app: "KeyHunter"

    class Save(Message):
        def __init__(self) -> None:
            super().__init__()

    class Update(Message):
        def __init__(self, setting: SettingUpdateInfo) -> None:
            super().__init__()
            self.setting = setting

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
        settings: AppSettings = self.app.settings

        # App settings
        themes = [
            theme for theme in self.app.available_themes if theme != "textual-ansi"
        ]
        theme = self.app.theme
        with Center():
            yield SelectSetting(
                id="theme",
                label="Theme",
                values=themes,
                default=theme,
            )
        yield Rule(line_style="none")

        # Typing settings
        typer_settings = settings.typer
        values = [engine.value for engine in TyperEngine]
        with Center():
            yield SelectSetting(
                id=constants.TYPER_ENGINE,
                label="Typer",
                values=values,
                default=typer_settings.typer_engine.value,
            )
        yield Rule(line_style="none")

        typer_borders = list(TyperBorder.__args__)
        with Center():
            yield SelectSetting(
                id=constants.TYPER_BORDER,
                label="Border",
                values=typer_borders,
                default=typer_settings.border,
            )
        yield Rule(line_style="none")

        typer = TyperSimulator(
            settings=settings, id="setting-typer", classes="setting-typer"
        )
        typer.can_focus = False
        typer.simulate()
        with Center():
            yield typer

        yield Rule(line_style="none")

        sle_settings = typer_settings.single_line_engine
        sle_width_validator = Number(
            minimum=sle_settings.min_width, maximum=sle_settings.max_width
        )
        with Container(id="sle-container", classes="height-auto"):
            with Center():
                yield SwitchSetting(
                    id=constants.SLE_PRE_CONTENT_SPACE,
                    label="Pre content space",
                    default=sle_settings.enable_pre_content_space,
                )
            yield Rule(line_style="none")

            with Center():
                yield InputSetting(
                    id=constants.SLE_WIDTH,
                    label="Width",
                    default=sle_settings.width,
                    validators=[sle_width_validator],
                )

        se_settings = typer_settings.standard_engine
        se_width_validator = Number(
            minimum=se_settings.min_width, maximum=se_settings.max_width
        )
        se_height_validator = Number(
            minimum=se_settings.min_height, maximum=se_settings.max_height
        )
        with Container(id="se-container", classes="height-auto"):
            with Center():
                yield InputSetting(
                    id=constants.SE_WIDTH,
                    label="Width",
                    default=se_settings.width,
                    validators=[se_width_validator],
                )
            yield Rule(line_style="none")
            with Center():
                yield InputSetting(
                    id=constants.SE_HEIGHT,
                    label="Height",
                    default=se_settings.height,
                    validators=[se_height_validator],
                )
        yield Rule(line_style="none")

        # Content settings
        content_settings = settings.content
        with Center():
            yield SelectSetting(
                id=constants.CONTENT_TYPE,
                label="Content type",
                values=[ct.value for ct in ContentType],
                default=content_settings.content_type.value,
            )
        yield Rule(line_style="none")

        content_lenght_validator = Number(minimum=20, maximum=1000)
        with Container(id="simple_content_type_settings", classes="height-auto"):
            with Center():
                yield InputSetting(
                    id=constants.CONTENT_LENGHT,
                    label="Content lenght",
                    default=content_settings.content_lenght,
                    validators=[content_lenght_validator],
                )

        with Center():
            yield Button(label="save", id="save", compact=True)

    def on_mount(self) -> None:
        settings = self.app.settings
        self._toggle_typer_engine_settings(settings.typer.typer_engine)
        self._toggle_content_settings(settings.content.content_type)

    def _toggle_content_settings(self, content_type: ContentType) -> None:
        container = self.query_one("#simple_content_type_settings")
        if content_type == ContentType.COMMON:
            container.remove_class("hidden")
        else:
            container.add_class("hidden")

    def _toggle_typer_engine_settings(self, typer_engine: TyperEngine) -> None:
        match typer_engine:
            case TyperEngine.SINGLE_LINE:
                container_to_show = "#sle-container"
                container_to_hide = "#se-container"
            case TyperEngine.STANDARD:
                container_to_show = "#se-container"
                container_to_hide = "#sle-container"

        self.query_one(container_to_show).remove_class("hidden")
        self.query_one(container_to_hide).add_class("hidden")

    @on(events.Focus)
    def handle_focus(self) -> None:
        for child_widget in self.walk_children(Widget):
            if child_widget.can_focus:
                child_widget.focus()
                break

    @on(events.DescendantFocus)
    @on(events.DescendantBlur)
    def handle_descendant_focus(self) -> None:
        self.is_active = self.has_focus_within

    @on(SettingChanged)
    def update_settings(self, message: SettingChanged) -> None:
        message.stop()

        setting_name = message.name

        if setting_name == constants.TYPER_ENGINE:
            self._toggle_typer_engine_settings(TyperEngine(message.value))
        elif setting_name == constants.CONTENT_TYPE:
            self._toggle_content_settings(ContentType(message.value))

        if setting_name in self.invalid_settings:
            self.invalid_settings.remove(setting_name)
            self.mutate_reactive(Settings.invalid_settings)

        self.post_message(self.Update(SettingUpdateInfo(setting_name, message.value)))

    @on(InvalidSetting)
    def update_invalid_settings(self, message: InvalidSetting) -> None:
        message.stop()
        self.invalid_settings.add(message.name)
        self.mutate_reactive(Settings.invalid_settings)

    @on(Button.Pressed, "#save")
    def save_settings(self, message: Button.Pressed) -> None:
        message.stop()
        self.post_message(self.Save())
