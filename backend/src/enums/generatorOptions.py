from enum import Enum


class SupportedLanguage(str, Enum):
    german = "de"
    english = "en"


class GeneratorMode(str, Enum):
    practice = "PRACTICE"
    definitions = "DEFINITIONS"
    # mc = "MULTIPLE_CHOICE"
    # open_ended = "OPEN_ENDED"


class ExportFormat(str, Enum):
    anki = "apkg"
    csv = "csv"
