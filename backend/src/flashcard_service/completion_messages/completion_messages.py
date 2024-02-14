class Messages:
    """
    A class representing a structured message sequence for the flashcard generation system.

    Parameters
    ----------
    system : str
        The system prompts.
    example_user : str
        The example user prompts.
    example_assistant : str
        The example assistant response.
    input_text : str
        The input text provided by the user.

    Attributes
    ----------
    _messages : list
        A list of messages, each message being a dictionary with 'role' and 'content'.
    _index : int
        An index for iterating over the messages.
    """

    def __init__(self, system: str, example_user: str, example_assistant: str, input_text: str):
        self.system = system
        self.example_user = example_user
        self.example_assistant = example_assistant
        self.input_text = input_text
        self._messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": self.example_user},
            {"role": "assistant", "content": self.example_assistant},
            {"role": "user", "content": self.input_text},
        ]
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._messages):
            result = self._messages[self._index]
            self._index += 1
            return result
        else:
            self._index = 0
            raise StopIteration

    def as_message_list(self) -> list:
        """
        Converts the Message object to a list of messages.

        Returns
        -------
        list
            A list of messages, each message being a dictionary with 'role' and 'content'.
        """
        return self._messages

    def compute_prompt_tokens(self, encoding) -> int:
        """
        Computes the total number of tokens in the prompts messages (excluding the actual input text).

        Parameters
        ----------
        encoding : tiktoken.Encoding
            Encoding object for the desired model.

        Returns
        -------
        int
            Total number of tokens in the prompts messages (excluding the actual input text).
        """
        base_count = 18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role']))
             for message in self._messages[:-1]]
        )
        return base_count

    def compute_input_tokens(self, encoding) -> int:
        """
        Computes the total number of tokens in the input text.

        Parameters
        ----------
        encoding : tiktoken.Encoding
            Encoding object for the desired model.

        Returns
        -------
        int
            Total number of tokens in the input text.
        """
        return len(encoding.encode(self._messages[-1]['content'])) + len(encoding.encode(self._messages[-1]['role']))

    def compute_total_tokens(self, encoding) -> int:
        """
        Computes the total number of tokens including the input text.

        Parameters
        ----------
        encoding : tiktoken.Encoding
            Encoding object for the desired model.

        Returns
        -------
        int
            Total number of tokens including the input text.
        """
        total_count = self.compute_prompt_tokens(encoding) + self.compute_input_tokens(encoding)
        return total_count
