from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Select, SelectionList

from keyhunter import const as CONST
from keyhunter.content.schemas import (
    ContentType,
    NaturalLanguage,
    NaturalLanguageCategory,
)
from keyhunter.settings.commands import (
    SetContentTypeCommand,
    SetNaturalLanguageCategoryCommand,
    SetNaturalLanguageCommand,
    SetNaturalLanguageContentCommand,
    SetNaturalLanguageWordsCountCommand,
)
from keyhunter.settings.messages import SettingChanged

from .components import SelectSetting, LinearSliderSetting

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class ContentTypeSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_type = self.app.settings.content.content_type.value
        available_content_types = [ct.value for ct in ContentType]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetContentTypeCommand,
                id="content-type",
                label="Content type",
                values=available_content_types,
                default=content_type,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content,
            CONST.CONTENT_TYPE_KEY,
            self._on_content_type_changed,
            init=False,
        )

    def _on_content_type_changed(self, content_type: ContentType) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = content_type


class NaturalLanguageSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        language = self.app.settings.content.natural_language.language.value
        available_languages = [lang.value for lang in NaturalLanguage]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetNaturalLanguageCommand,
                id="natural-language",
                label="Language",
                values=available_languages,
                default=language,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.natural_language,
            CONST.LANGUAGE_KEY,
            self._on_language_changed,
            init=False,
        )

    def _on_language_changed(self, language: NaturalLanguage) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = language


class NaturalLanguageCategorySelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        category = self.app.settings.content.natural_language.category.value
        available_categories = [c.value for c in NaturalLanguageCategory]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                command=SetNaturalLanguageCategoryCommand,
                id="natural-language-category",
                label="Category",
                values=available_categories,
                default=category,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.natural_language,
            CONST.CATEGORY_KEY,
            self._on_category_changed,
            init=False,
        )

    def _on_category_changed(self, category: NaturalLanguageCategory) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = category


class CommonWordsContent(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_files = self.app.content_service.category_files(
            "natural_language",
            self.app.settings.content.natural_language.language.name.lower(),
            "common_words",
        )
        selected = self.app.settings.content.natural_language.common_words.content_files
        selections = [
            (ct, ct, True if ct in selected else False) for ct in content_files
        ]
        sl = SelectionList(*selections)
        sl.border_title = "Words from"
        yield sl

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        if not event.control.selected:
            self.notify("Please select at least one source")
        else:
            self.post_message(
                SettingChanged(
                    command=SetNaturalLanguageContentCommand(event.control.selected)
                )
            )


class CommonWordsCountContainer(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.content.natural_language.common_words
        yield LinearSliderSetting(
            positions_count=10,
            current_value=settings.words_count,
            min_value=settings.min_words_count,
            max_value=settings.max_words_count,
            command=SetNaturalLanguageWordsCountCommand,
            id="common-words-count-setting",
            label="Words in session",
        )


class CommonWordsSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield CommonWordsContent(classes="setting-container")
        yield CommonWordsCountContainer(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.natural_language,
            CONST.CATEGORY_KEY,
            self._toggle_container_visibility,
        )

    def _toggle_container_visibility(self, content_mode: ContentType) -> None:
        if content_mode == NaturalLanguageCategory.COMMON:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class NaturalLanguageSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield NaturalLanguageSelector(classes="setting-container")
        yield NaturalLanguageCategorySelector(classes="setting-container")
        yield CommonWordsSettingsContainer()

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content,
            CONST.CONTENT_TYPE_KEY,
            self._toggle_container_visibility,
        )

    def _toggle_container_visibility(self, content_mode: ContentType) -> None:
        if content_mode == ContentType.NATURAL:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class ContentSettingsContainer(VerticalGroup):
    BORDER_TITLE = "Content"

    def compose(self) -> ComposeResult:
        yield ContentTypeSelector(classes="setting-container")
        yield NaturalLanguageSettingsContainer()
