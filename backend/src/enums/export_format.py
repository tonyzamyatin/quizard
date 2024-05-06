from enum import Enum


class ExportFormat(str, Enum):
    apkg = "anki"
    csv = "csv"
