from textual.message import Message


class SettingChanged(Message):
    def __init__(self, command) -> None:
        super().__init__()
        self.command = command
