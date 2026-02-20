import random
from importlib import resources

from keyhunter.settings.schemas import ContentSettings

from .schemas import ContentType


class ContentService:
    def __init__(self, settings: ContentSettings) -> None:
        self.content_type = settings.content_type
        self.language = settings.language
        self.content_lenght = settings.content_lenght

    def generate(self) -> str:
        content_files = resources.files("keyhunter.content.datasets")

        match self.content_type:
            case ContentType.SIMPLE:
                text = (
                    content_files.joinpath(self.language.value)
                    .joinpath("simple.txt")
                    .read_text()
                )
                text = text.split("\n")
                return random.choice(text)
            case ContentType.COMMON:
                text = (
                    content_files.joinpath(self.language.value)
                    .joinpath("common_1000.txt")
                    .read_text()
                )
                words = text.split()
                random.shuffle(words)
                return "\n".join(words[: self.content_lenght])

    @property
    def placeholder(self) -> str:
        return "Press 'space' to start typing"
