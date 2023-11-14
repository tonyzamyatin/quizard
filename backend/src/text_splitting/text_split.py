import tiktoken
from backend.src.custom_exceptions.quizard_exceptions import PromptSizeError, ConfigInvalidValueError


def calculate_window_size(base_prompt_size: int, config: dict):
    if base_prompt_size < config["4k_model"]["base_prompt_limit"]:
        return 4000 - base_prompt_size - config["4k_model"]["completion_limit"]
    # TODO: Decide what to do with the 16k model config after OpenAI API update.
    # elif base_prompt_size < config["16k_model"]["base_prompt_limit"]:
    #     return 16000 - base_prompt_size - config["16k_model"]["completion_limit"]
    else:
        raise PromptSizeError(
            f"The base prompt size of {base_prompt_size} exceeds the allowed base prompt limit. "
            "You may need to adjust the base prompt size, base prompt limit, or the completion limit."
        )


def split_text(model_name: str, text: str, base_prompt_size: int, config: dict):
    window_size = calculate_window_size(base_prompt_size, config)
    overlap_type = config['text_splitting']['window_overlap_type']
    if overlap_type == 'absolute':
        window_overlap = config['text_splitting']['absolute_window_overlap']
    elif overlap_type == 'relative':
        window_overlap = window_size * config['text_splitting']['relative_window_overlap']
    else:
        raise ConfigInvalidValueError(f"The window_overlap_type specified in the run_config must be either 'absolute' or 'relative' but it was '{overlap_type}'")
    encoding = tiktoken.encoding_for_model(model_name)
    encoded_text = encoding.encode(text)
    fragments = []

    current_start = 0
    while current_start < len(encoded_text):
        current_fragment = encoded_text[current_start:current_start + window_size]
        fragments.append(encoding.decode(current_fragment))
        current_start += int(window_size - window_overlap)

    return fragments
