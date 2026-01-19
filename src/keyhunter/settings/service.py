from enum import StrEnum
from typing import Any

import yaml
from xdg_base_dirs import xdg_config_home

from .schemas import AppSettings

yaml.SafeDumper.add_multi_representer(
    StrEnum,
    lambda dumper, data: dumper.represent_scalar(
        "tag:yaml.org,2002:str",
        data.value,
    ),
)


class SettingsService:
    def __init__(self) -> None:
        self.config_path = xdg_config_home() / "keyhunter" / "settings.yml"
        self._settings = self._load()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    @property
    def default(self) -> AppSettings:
        return AppSettings()

    def _load(self) -> AppSettings:
        try:
            if not self.config_path.exists():
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                self.config_path.touch()
                self._settings = AppSettings()
                self.save()
                return self._settings
            else:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return AppSettings.model_validate(yaml.safe_load(f))
        except Exception:
            return AppSettings()

    def update(self, data: tuple[str, Any]) -> AppSettings:
        settings = self._settings.model_dump()

        current = settings
        parts = data[0].split(".")
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = data[1]

        self._settings = AppSettings.model_validate(settings)
        return self._settings

    def save(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._settings.model_dump(), f)
