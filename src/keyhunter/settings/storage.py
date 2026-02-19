import json
from typing import Any

from platformdirs import user_config_path


class SettingsStorage:
    def __init__(self) -> None:
        self._config_path = (
            user_config_path("keyhunter", ensure_exists=True) / "settings.json"
        )

    def load(self) -> dict[str, Any]:
        raw_json = self._config_path.resolve().read_text()
        return json.loads(raw_json)

    def save(self, settings: dict[str, Any]) -> None:
        raw_json = json.dumps(settings)
        self._config_path.resolve().write_text(raw_json)
