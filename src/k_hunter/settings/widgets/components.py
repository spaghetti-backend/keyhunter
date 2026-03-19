from typing import Any, Callable, ClassVar, Literal

from rich.style import Style
from textual import on
from textual.app import ComposeResult, RenderResult
from textual.binding import Binding, BindingType
from textual.color import Gradient
from textual.containers import HorizontalGroup
from textual.message import Message
from textual.renderables.bar import Bar as BarRenderable
from textual.validation import Validator
from textual.widgets import Input, Label, ProgressBar, Select, SelectionList, Switch
from textual.widgets._progress_bar import Bar
from textual.widgets._select import SelectOverlay

from k_hunter.settings.commands import SetSettingCommand
from k_hunter.settings.messages import SettingChanged
from k_hunter.settings.schemas import BaseSettings


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
        id: str,
        target: BaseSettings,
        attr_name: str,
        label: str,
        values: list[str],
        default: str | None = None,
        allow_blank: bool = False,
        cast: Callable[[Any], Any] | None = None,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.values = values
        self.default = default
        self.allow_blank = allow_blank
        self._target = target
        self._attr_name = attr_name
        self._cast = cast

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
                command=SetSettingCommand(
                    target=self._target,
                    attr_name=self._attr_name,
                    value=event.value,
                    cast=self._cast,
                ),
            )
        )


class InputSetting(HorizontalGroup):
    def __init__(
        self,
        id: str,
        target: BaseSettings,
        attr_name: str,
        label: str,
        default: str | int | float,
        validators: list[Validator],
        cast: Callable[[Any], Any] | None = None,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.default = default
        self.validators = validators
        self._current_value = str(default)
        self._target = target
        self._attr_name = attr_name
        self._cast = cast

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
                    command=SetSettingCommand(
                        target=self._target,
                        attr_name=self._attr_name,
                        value=self._convert_to_default_type(new_value),
                        cast=self._cast,
                    ),
                )
            )
            self._current_value = new_value


class SwitchSetting(HorizontalGroup):
    def __init__(
        self,
        id: str,
        target: BaseSettings,
        attr_name: str,
        label: str,
        default: bool,
        cast: Callable[[Any], Any] | None = None,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.default = default
        self._target = target
        self._attr_name = attr_name
        self._cast = cast

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
                command=SetSettingCommand(
                    target=self._target,
                    attr_name=self._attr_name,
                    value=event.value,
                    cast=self._cast,
                ),
            )
        )


class ThumbStyle(BarRenderable):
    HALF_BAR_LEFT: str = "▐"
    BAR: str = "█"
    HALF_BAR_RIGHT: str = "▌"


class Thumb(Bar):
    def __init__(
        self,
        total_positions: float,
        *,
        id: str | None = None,
        classes: str | None = None,
        gradient: Gradient | None = None,
    ):
        super().__init__(
            id=id,
            classes=classes,
            gradient=gradient,
            bar_renderable=ThumbStyle,
        )
        self.thumb_ratio = 1 / total_positions

    def render(self) -> RenderResult:
        """Render the bar with the correct portion filled."""
        if self.percentage is None:
            return self.render_indeterminate()
        else:
            bar_style = self.get_component_rich_style("bar--bar")

            return self.bar_renderable(
                highlight_range=(
                    self.percentage * self.size.width,
                    (self.percentage + self.thumb_ratio) * self.size.width,
                ),
                highlight_style=Style.from_color(bar_style.color),
                background_style=Style.from_color(bar_style.bgcolor),
                gradient=self.gradient,
            )


class LinearSlider(ProgressBar, can_focus=True):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("minus,h,left", "decrease", "Decrease"),
        Binding("plus,l,right,equals_sign", "increase", "Increase"),
    ]

    class Changed(Message):
        def __init__(self, value: int) -> None:
            super().__init__()
            self.value: int = value

    def __init__(
        self,
        *,
        positions_count: int,
        current_value: int,
        min_value: int,
        max_value: int,
        id: str | None = None,
        classes: str | None = None,
        gradient: Gradient | None = None,
    ):
        super().__init__(
            positions_count,
            id=id,
            classes=classes,
            gradient=gradient,
        )
        if positions_count < 3:
            raise ValueError("Minimum three positions")

        self._positions_count = positions_count
        self._min_value = min_value
        self._max_value = max_value
        self._step = (self._max_value - self._min_value) / (self._positions_count - 1)
        self._current_position = self._compute_position(current_value)

    def compose(self) -> ComposeResult:
        yield Thumb(total_positions=self._positions_count, id="bar").data_bind(
            ProgressBar.percentage
        ).data_bind(ProgressBar.gradient)

    def on_mount(self) -> None:
        super().on_mount()
        self.update(advance=self._current_position)

    def action_increase(self) -> None:
        if self._current_position < self._positions_count - 1:
            self.update(advance=1)
            self._current_position += 1
            self.post_message(self.Changed(self._compute_value()))

    def action_decrease(self) -> None:
        if self._current_position > 0:
            self.update(advance=-1)
            self._current_position -= 1
            self.post_message(self.Changed(self._compute_value()))

    def set_value(self, value: int) -> None:
        if value == self._compute_value():
            return
        self._current_position = self._compute_position(value)
        self.update(
            progress=self._current_position,
        )

    def _compute_value(self) -> int:
        if self._current_position == 0 or self._positions_count <= 1:
            return self._min_value
        elif self._current_position == self._positions_count - 1:
            return self._max_value
        else:
            return self._min_value + int(round(self._current_position * self._step))

    def _compute_position(self, current_value: int) -> int:
        if current_value == self._min_value:
            return 0
        elif current_value == self._max_value:
            return self._positions_count - 1
        else:
            return int(round((current_value - self._min_value) / self._step))


class LinearSliderSetting(HorizontalGroup):
    def __init__(
        self,
        positions_count: int,
        current_value: int,
        min_value: int,
        max_value: int,
        id: str,
        label: str,
        target: BaseSettings,
        attr_name: str,
        cast: Callable[[Any], Any] | None = None,
    ) -> None:
        super().__init__(id=id, classes="setting-row")
        self.label = label
        self.positions_count = positions_count
        self.current_value = current_value
        self._min_value = min_value
        self._max_value = max_value
        self._target = target
        self._attr_name = attr_name
        self._cast = cast

    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="setting-label")
        yield Label(
            f"{self.current_value:>3}",
            id="slider-value-label",
            classes="slider-value-label",
        )
        yield LinearSlider(
            positions_count=self.positions_count,
            current_value=self.current_value,
            min_value=self._min_value,
            max_value=self._max_value,
        )

    def on_linear_slider_changed(self, event: LinearSlider.Changed) -> None:
        self.query_one("#slider-value-label", Label).update(f"{event.value:>3}")
        self.post_message(
            SettingChanged(
                SetSettingCommand(
                    target=self._target,
                    attr_name=self._attr_name,
                    value=event.value,
                    cast=self._cast,
                )
            )
        )


class VimSelectionList(SelectionList):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
    ]

    def action_cursor_down(self) -> None:
        if self.highlighted == len(self.options) - 1:
            self.screen.focus_next()
            return
        else:
            return super().action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.highlighted == 0:
            self.screen.focus_previous()
        else:
            return super().action_cursor_up()
