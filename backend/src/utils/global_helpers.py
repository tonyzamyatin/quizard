import os


def format_num(number: int) -> str:
    """Formats an integer by adding a dot every three digits."""
    reversed_str = str(number)[::-1]
    formatted_str = '.'.join(reversed_str[i:i + 3] for i in range(0, len(reversed_str), 3))
    return formatted_str[::-1]


def write_to_log(message: str):
    """Write to the logs and also print the message."""
    with open(os.getenv('LOG_FILE', default='logs/logs.txt'), 'a') as f:
        f.write(message + '\n')
    print(message)
