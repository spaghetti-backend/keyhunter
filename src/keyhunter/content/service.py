import random
from importlib import resources
from importlib.abc import Traversable

from keyhunter import const as CONST
from keyhunter.settings.schemas import ContentSettings

from .schemas import ContentType, NaturalLanguageCategory, ProgrammingLanguageCategory


class ContentService:
    def __init__(self, settings: ContentSettings) -> None:
        self.settings = settings
        self.content_files = resources.files(CONST.DATASETS_STORAGE_PATH)
        self.content_mapping = self._glob(self.content_files)

    def _glob(self, dir: Traversable) -> dict:

        rd = {}
        for sd in dir.iterdir():
            if sd.is_dir():
                rd[sd.name] = self._glob(sd)
            else:
                rd[sd.name] = sd

        return rd

    # Remove if not needed after release 1.0
    #
    # def content_types(self) -> list[str]:
    #     return [ct.capitalize().replace("_", " ") for ct in self.content_mapping.keys()]
    #
    # def languages(self, mode: str) -> list[str]:
    #     return list(self.content_mapping[mode].keys())
    #
    # def categories(self, mode: str, language: str) -> list[str]:
    #     return list(self.content_mapping[mode][language].keys())

    def category_files(
        self, content_type: str, language: str, category: str
    ) -> list[str]:
        return sorted(self.content_mapping[content_type][language][category].keys())

    def generate(self) -> str:
        match self.settings.content_type:
            case ContentType.NATURAL:
                return self._natural_language_text()
            case ContentType.PRAGRAMMING:
                return self._programming_language_text()

    def _natural_language_text(self) -> str:
        match self.settings.natural_language.category:
            case NaturalLanguageCategory.SIMPLE:
                return self._natural_language_simple_text()
            case NaturalLanguageCategory.COMMON:
                return self._natural_language_common_words()

    def _natural_language_simple_text(self) -> str:
        text = (
            self.content_files.joinpath(CONST.NATURAL_LANGUAGE_KEY)
            .joinpath(self._language_dir())
            .joinpath(CONST.SIMPLE_FILENAME)
            .read_text()
        )
        text = text.split("\n")
        return random.choice(text)

    def _natural_language_common_words(self) -> str:
        common_words = []
        content_files = self.settings.natural_language.common_words.content_files
        if not content_files:
            content_files = self.category_files(
                CONST.NATURAL_LANGUAGE_KEY,
                self.settings.natural_language.language.name.lower(),
                CONST.COMMON_DIR,
            )

        for filename in content_files:
            text = (
                self.content_files.joinpath(CONST.NATURAL_LANGUAGE_KEY)
                .joinpath(self._language_dir())
                .joinpath(CONST.COMMON_DIR)
                .joinpath(filename)
                .read_text()
            )
            common_words.extend(text.split())
        random.shuffle(common_words)

        words_count = self.settings.natural_language.common_words.words_count
        upper_percent = self.settings.natural_language.common_words.upper_percent

        words = [
            word.capitalize() if random.randint(0, 100) < upper_percent else word
            for word in common_words[:words_count]
        ]

        return "\n".join(words)

    def _programming_language_text(self) -> str:
        match self.settings.programming_language.category:
            case ProgrammingLanguageCategory.KEYWORDS:
                return self._programming_language_keywords()
            case ProgrammingLanguageCategory.CODE:
                return self._programming_language_code_samples()

    def _programming_language_keywords(self) -> str:
        keywords = []
        content_files = self.settings.programming_language.keywords.content_files
        if not content_files:
            content_files = self.category_files(
                CONST.PROGRAMMING_LANGUAGE_KEY,
                self.settings.programming_language.language.name.lower(),
                CONST.COMMON_DIR,
            )

        for filename in content_files:
            text = (
                self.content_files.joinpath(CONST.PROGRAMMING_LANGUAGE_KEY)
                .joinpath(self._language_dir())
                .joinpath(CONST.COMMON_DIR)
                .joinpath(filename)
                .read_text()
            )
            keywords.extend(text.split())

        keywords_count = self.settings.programming_language.keywords.keywords_count
        while len(keywords) < keywords_count:
            keywords.extend(keywords)

        random.shuffle(keywords)
        return "\n".join(random.choices(keywords, k=keywords_count))

    def _programming_language_code_samples(self) -> str:
        return "Available after adding CodeEngine"

    def _language_dir(self) -> str:
        match self.settings.content_type:
            case ContentType.NATURAL:
                settings = self.settings.natural_language
            case ContentType.PRAGRAMMING:
                settings = self.settings.programming_language
        return settings.language.name.lower()

    @property
    def placeholder(self) -> str:
        return "Press 'space' to start typing"
