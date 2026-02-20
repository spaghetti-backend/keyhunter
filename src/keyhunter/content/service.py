import random
from importlib import resources

from keyhunter import const as CONST
from keyhunter.settings.schemas import ContentSettings

from .schemas import ContentType


class ContentService:
    def __init__(self, settings: ContentSettings) -> None:
        self.content_type = settings.content_type
        self.language = settings.language
        self.content_lenght = settings.content_lenght

    def generate(self) -> str:
        content_files = resources.files(CONST.DATASETS_STORAGE_PATH)

        match self.content_type:
            case ContentType.SIMPLE:
                text = (
                    content_files.joinpath(self.language.name.lower())
                    .joinpath(CONST.SIMPLE_FILENAME)
                    .read_text()
                )
                text = text.split("\n")
                return random.choice(text)
            case ContentType.COMMON:
                text = (
                    content_files.joinpath(self.language.name.lower())
                    .joinpath(CONST.COMMON_WORDS_FILENAME)
                    .read_text()
                )
                words = text.split()
                random.shuffle(words)
                return "\n".join(words[: self.content_lenght])

    @property
    def placeholder(self) -> str:
        return "Press 'space' to start typing"
