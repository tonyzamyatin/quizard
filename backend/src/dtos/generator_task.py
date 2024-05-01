from pydantic import BaseModel

from src.dtos.immutable_dto import ImmutableBaseModel
from src.enums.export_format import ExportFormat
from src.enums.generation_mode import GeneratorMode
from src.enums.language import SupportedLanguage


class FlashcardGeneratorTaskDto(ImmutableBaseModel):
    """
    Data transfer object for flashcard generation requests.
    Note: Pydantic automatically converts string values to the corresponding enum values.
    lang : LanguageEnum
        Language of the flashcards. Must valid and a supported language.
    mode : ModeEnum
        Mode of flashcard generation. Must valid and a supported mode.
    export_format : ExportFormatEnum
        Format in which to export the generated flashcards. Must be a valid and supported format.
    input_text : str
        The text input from which flashcards are generated.
    """
    lang: SupportedLanguage
    mode: GeneratorMode
    export_format: ExportFormat
    input_text: str
