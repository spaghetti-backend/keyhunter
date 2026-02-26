from .commands import SetSettingCommand
from .schemas import AppSettings
from .storage import SettingsStorage


class SettingsService:
    def __init__(self, settings: AppSettings) -> None:
        self._history: list[SetSettingCommand] = []
        self._storage = SettingsStorage()
        self._settings = settings

        user_settings = self._storage.load()
        self._settings.load(user_settings)
        self._saved = True

    @property
    def has_updates(self) -> bool:
        for command in self._history:
            if command.executed:
                return True
        return False

    @property
    def saved(self) -> bool:
        return self._saved

    def update(self, command: SetSettingCommand):
        command.execute()
        self._history.append(command)
        self._saved = False

    def undo(self) -> None:
        for command in reversed(self._history):
            if command.executed:
                command.undo()
                self._saved = False
                break

    def restore(self) -> None:
        for command in reversed(self._history):
            command.undo()
            self._saved = False

    def reset_to_default(self) -> None:
        self.restore()
        self._settings.load({}, set_reactive=False)
        self._saved = False

    def save(self) -> None:
        self._storage.save(self._settings.dump())
        self._history.clear()
        self._saved = True
