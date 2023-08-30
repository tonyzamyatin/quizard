import tiktoken
# splits the text in multiple text splices, by taking take_amount tokens at every token_step
# recommended values for gpt-3.5 4k: token_step: 2500, take_amount: 3000
def split_text(text, token_step, take_amount):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    encoded_text = encoding.encode(text)

    splits = []
    # loop as long as there is still remaining text after the last 500 token window
    current_start = 0
    while current_start < len(encoded_text):
        current_text = encoded_text[current_start:current_start + take_amount]
        splits.append(encoding.decode(current_text))
        current_start += token_step
    return splits
