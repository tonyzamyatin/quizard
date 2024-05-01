from enum import Enum


class ExportFormat(str, Enum):
    anki = "apkg"
    csv = "csv"
