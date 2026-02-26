from typing import Any, Callable

from .schemas import BaseSettings


class SetSettingCommand:
    def __init__(
        self,
        target: BaseSettings,
        attr_name: str,
        value: Any,
        cast: Callable[[Any], Any] | None = None,
    ) -> None:
        self._target = target
        self._attr_name = attr_name
        self._value = value
        self._cast = cast
        self._executed = False

    @property
    def executed(self) -> bool:
        return self._executed

    def execute(self) -> None:
        if not self._executed:
            self._old_value = getattr(self._target, self._attr_name)
            value = self._cast(self._value) if self._cast else self._value
            setattr(self._target, self._attr_name, value)
            self._executed = True

    def undo(self) -> None:
        if self._executed:
            setattr(self._target, self._attr_name, self._old_value)
            self._executed = False
