from typing import Any

from textual.message import Message


class SettingChanged(Message):
    def __init__(self, name: str, value: Any) -> None:
        super().__init__()
        self.name = name
        self.value = value


class InvalidSetting(Message):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
