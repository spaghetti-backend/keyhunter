from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Select, SelectionList

from keyhunter import const as CONST
from keyhunter.content.schemas import (
    ContentType,
    NaturalLanguage,
    NaturalLanguageCategory,
    ProgrammingLanguage,
    ProgrammingLanguageCategory,
)
from keyhunter.settings.commands import SetSettingCommand
from keyhunter.settings.messages import SettingChanged

from .components import LinearSlider, LinearSliderSetting, SelectSetting

if TYPE_CHECKING:
    from keyhunter.main import KeyHunter


class ContentTypeSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_type = self.app.settings.content.content_type.value
        available_content_types = [ct.value for ct in ContentType]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                id="content-type",
                label="Content type",
                values=available_content_types,
                default=content_type,
                target=self.app.settings.content,
                attr_name=CONST.CONTENT_TYPE_KEY,
                cast=ContentType,
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
                id="natural-language",
                label="Language",
                values=available_languages,
                default=language,
                target=self.app.settings.content.natural_language,
                attr_name=CONST.LANGUAGE_KEY,
                cast=NaturalLanguage,
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
                id="natural-language-category",
                label="Category",
                values=available_categories,
                default=category,
                target=self.app.settings.content.natural_language,
                attr_name=CONST.CATEGORY_KEY,
                cast=NaturalLanguageCategory,
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
    # TODO: Add watcher
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_files = self.app.content_service.category_files(
            CONST.NATURAL_LANGUAGE_KEY,
            self.app.settings.content.natural_language.language.name.lower(),
            CONST.COMMON_DIR,
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
                    command=SetSettingCommand(
                        target=self.app.settings.content.natural_language.common_words,
                        attr_name=CONST.CONTENT_FILES_KEY,
                        value=event.control.selected,
                    )
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
            id="common-words-count-setting",
            label="Words in session",
            target=self.app.settings.content.natural_language.common_words,
            attr_name=CONST.WORDS_COUNT_KEY,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.natural_language.common_words,
            CONST.WORDS_COUNT_KEY,
            self._on_common_words_count_changed,
            init=False,
        )

    def _on_common_words_count_changed(self, words_count: int) -> None:
        with self.prevent(LinearSlider.Changed):
            self.query_one(LinearSlider).set_value(words_count)


class ProgrammingLanguageSelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        language = self.app.settings.content.programming_language.language.value
        available_languages = [lang.value for lang in ProgrammingLanguage]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                id="programming-language",
                label="Language",
                values=available_languages,
                default=language,
                target=self.app.settings.content.programming_language,
                attr_name=CONST.LANGUAGE_KEY,
                cast=ProgrammingLanguage,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.programming_language,
            CONST.LANGUAGE_KEY,
            self._on_language_changed,
            init=False,
        )

    def _on_language_changed(self, language: ProgrammingLanguage) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = language


class ProgrammingLanguageCategorySelector(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        category = self.app.settings.content.programming_language.category.value
        available_categories = [c.value for c in ProgrammingLanguageCategory]
        with self.prevent(Select.Changed):
            yield SelectSetting(
                id="programming-language-category",
                label="Category",
                values=available_categories,
                default=category,
                target=self.app.settings.content.programming_language,
                attr_name=CONST.CATEGORY_KEY,
                cast=ProgrammingLanguageCategory,
            )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.programming_language,
            CONST.CATEGORY_KEY,
            self._on_category_changed,
            init=False,
        )

    def on_setting_changed(self, event) -> None:
        event.stop()
        self.notify("Available after adding CodeEngine", severity="warning", timeout=4)
        self._on_category_changed(ProgrammingLanguageCategory.KEYWORDS)

    def _on_category_changed(self, category: ProgrammingLanguageCategory) -> None:
        with self.prevent(Select.Changed):
            self.query_one(Select).value = category


class CommonKeywordsContent(HorizontalGroup):
    # TODO: Add watcher
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        content_files = self.app.content_service.category_files(
            CONST.PROGRAMMING_LANGUAGE_KEY,
            self.app.settings.content.programming_language.language.name.lower(),
            CONST.COMMON_DIR,
        )
        selected = self.app.settings.content.programming_language.keywords.content_files
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
                    command=SetSettingCommand(
                        target=self.app.settings.content.programming_language.keywords,
                        attr_name=CONST.CONTENT_FILES_KEY,
                        value=event.control.selected,
                    )
                )
            )


class KeywordsCountContainer(HorizontalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        settings = self.app.settings.content.programming_language.keywords
        yield LinearSliderSetting(
            positions_count=10,
            current_value=settings.keywords_count,
            min_value=settings.min_keywords_count,
            max_value=settings.max_keywords_count,
            id="keywords-count-setting",
            label="Words in session",
            target=self.app.settings.content.programming_language.keywords,
            attr_name=CONST.KEYWORDS_COUNT_KEY,
        )

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.programming_language.keywords,
            CONST.KEYWORDS_COUNT_KEY,
            self._on_common_words_count_changed,
            init=False,
        )

    def _on_common_words_count_changed(self, keywords_count: int) -> None:
        with self.prevent(LinearSlider.Changed):
            self.query_one(LinearSlider).set_value(keywords_count)


class KeywordsSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield CommonKeywordsContent(classes="setting-container")
        yield KeywordsCountContainer(classes="setting-container")

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content.programming_language,
            CONST.CATEGORY_KEY,
            self._toggle_container_visibility,
        )

    def _toggle_container_visibility(
        self, category: ProgrammingLanguageCategory
    ) -> None:
        if category == ProgrammingLanguageCategory.KEYWORDS:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


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

    def _toggle_container_visibility(self, category: NaturalLanguageCategory) -> None:
        if category == NaturalLanguageCategory.COMMON:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")


class ProgrammingLanguageSettingsContainer(VerticalGroup):
    app: "KeyHunter"

    def compose(self) -> ComposeResult:
        yield ProgrammingLanguageSelector(classes="setting-container")
        yield ProgrammingLanguageCategorySelector(classes="setting-container")
        yield KeywordsSettingsContainer()

    def on_mount(self) -> None:
        self.watch(
            self.app.settings.content,
            CONST.CONTENT_TYPE_KEY,
            self._toggle_container_visibility,
        )

    def _toggle_container_visibility(self, content_mode: ContentType) -> None:
        if content_mode == ContentType.PRAGRAMMING:
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
        yield ProgrammingLanguageSettingsContainer()
