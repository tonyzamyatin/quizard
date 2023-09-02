import tiktoken


# splits the text in multiple text splices, by taking take_amount tokens at every token_step
# recommended values for gpt-3.5 4k: token_step: 2500, take_amount: 3000
def split_text(text: str, window_overlap: int, window_size: int):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    encoded_text = encoding.encode(text)

    fragments = []
    # loop as long as there is still remaining text after the last 500 token window
    current_start = 0
    while current_start < len(encoded_text):
        current_fragment = encoded_text[current_start:current_start + window_size]
        fragments.append(encoding.decode(current_fragment))
        current_start += (window_size - window_overlap)
    return fragments
