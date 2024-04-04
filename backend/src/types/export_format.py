from enum import Enum


class ExportFormatEnum(str, Enum):
    anki = "apkg"
    csv = "csv"
