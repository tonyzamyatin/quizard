from pydantic import BaseModel

from src.types.export_format import ExportFormatEnum
from src.types.generation_mode import ModeEnum
from src.types.language import LanguageEnum


class FlashcardGeneratorTaskDto(BaseModel):
    """
    Data transfer object for flashcard generation requests.
    lang : LanguageEnum
        Language of the flashcards. Must valid and a supported language.
    mode : ModeEnum
        Mode of flashcard generation. Must valid and a supported mode.
    export_format : ExportFormatEnum
        Format in which to export the generated flashcards. Must be a valid and supported format.
    input_text : str
        The text input from which flashcards are generated.
    """
    lang: LanguageEnum
    mode: ModeEnum
    export_format: ExportFormatEnum
    input_text: str
