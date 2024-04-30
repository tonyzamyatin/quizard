from enum import Enum


class ModeEnum(str, Enum):
    practice = "practice"
    definition = "definitions"
    mc = "mc"
    cloze = "cloze"
    open_ended = "open_ended"
