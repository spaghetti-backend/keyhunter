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

    @property
    def has_updates(self) -> bool:
        for command in self._history:
            if command.executed:
                return True
        return False

    def update(self, command: SetSettingCommand):
        command.execute()
        self._history.append(command)
        self.save()

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()
            self.save()

    def reset_to_default(self) -> None:
        self._history.clear()
        self._settings.load({}, set_reactive=False)
        self.save()

    def save(self) -> None:
        self._storage.save(self._settings.dump())
