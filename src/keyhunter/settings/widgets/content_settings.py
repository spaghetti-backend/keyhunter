from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.validation import Number
from textual.widgets import Input, Select

from keyhunter.content.schemas import ContentType, Language
from keyhunter.settings.commands import (
    SetContentLanguageCommand,
    SetContentLenghtCommand,
    SetContentTypeCommand,
)

from .components import InputSetting, SelectSetting

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class ContentLanguageSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_language = self.app.settings.content.language.value
        available_languages = [language.value for language in Language]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetContentLanguageCommand,
                id="content-language",
                label="Language",
                values=available_languages,
                default=content_language,
            )

    def _on_content_language_changed(self, content_language: Language) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = content_language


class ContentTypeSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_type = self.app.settings.content.content_type.value
        available_types = [content_type.value for content_type in ContentType]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetContentTypeCommand,
                id="content-type",
                label="Content type",
                values=available_types,
                default=content_type,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content,
            "_content_type",
            self._on_content_type_changed,
            init=False,
        )

    def _on_content_type_changed(self, content_type: ContentType) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = content_type


class ContentLength(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_settings = self.app.settings.content
        content_lenght = content_settings.content_lenght
        length_validator = Number(
            minimum=content_settings._min_content_lenght,
            maximum=content_settings._max_content_lenght,
        )
        yield InputSetting(
            command=SetContentLenghtCommand,
            id="content-lenght",
            label="Content lenght",
            default=content_lenght,
            validators=[length_validator],
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content,
            "_content_lenght",
            self._on_content_lenght_changed,
            init=False,
        )

    def _on_content_lenght_changed(self, content_lenght: int) -> None:
        with self.prevent(Input.Changed):
            self.query_one(Input).value = str(content_lenght)


class ContentSettingsContainer(VerticalGroup):
    BORDER_TITLE = "Content"

    def compose(self) -> ComposeResult:
        yield ContentLanguageSelector(classes="setting-container")
        yield ContentTypeSelector(classes="setting-container")
        yield ContentLength(classes="setting-container")
