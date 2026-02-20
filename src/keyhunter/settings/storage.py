import json
from typing import Any

from platformdirs import user_config_path

from keyhunter import const as CONST


class SettingsStorage:
    def __init__(self) -> None:
        self._config_path = (
            user_config_path(CONST.APP_NAME, ensure_exists=True)
            / CONST.SETTINGS_STORAGE_NAME
        )

    def load(self) -> dict[str, Any]:
        try:
            raw_json = self._config_path.resolve().read_text()
            return json.loads(raw_json)
        except FileNotFoundError:
            return {}

    def save(self, settings: dict[str, Any]) -> None:
        raw_json = json.dumps(settings)
        self._config_path.resolve().write_text(raw_json)
