from typing import List
import tiktoken
from src.custom_exceptions.quizard_exceptions import ConfigInvalidValueError


def split_text(encoding: tiktoken.Encoding, text: str, fragment_size: int, overlap_type: str, overlap: float) -> List[str]:
    """
    Split a given text into fragments based on specified encoding, fragment size, and overlap settings.

    Parameters
    ----------
    encoding : tiktoken.Encoding
        Encoding object for the desired model.
    text : str
        Text to be split into fragments.
    fragment_size : int
        Size of each text fragment in tokens.
    overlap_type : str
        Type of overlap ('absolute' or 'relative') used in text splitting.
    overlap : float
        Value of overlap. Interpreted as absolute or relative based on overlap_type.

    Returns
    -------
    List[str]
        List of text fragments.

    Raises
    ------
    ConfigInvalidValueError
        If the overlap type is neither 'absolute' nor 'relative'.
    """
    if overlap_type == 'absolute':
        abs_overlap = overlap
    elif overlap_type == 'relative':
        abs_overlap = fragment_size * overlap
    else:
        raise ConfigInvalidValueError(
            f"The overlap_type specified in the app configuration must be either 'absolute' or 'relative', but was '{overlap_type}'.")

    encoded_text = encoding.encode(text)
    fragments = []

    current_start = 0
    while current_start < len(encoded_text):
        current_end = current_start + fragment_size
        current_fragment = encoded_text[current_start:current_end]
        fragments.append(encoding.decode(current_fragment))
        current_start += int(fragment_size - abs_overlap)

    return fragments
