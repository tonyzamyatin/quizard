class Messages:
    def __init__(self, system: str, example_user: str, example_assistant: str, text_input):
        self.example_user = example_user
        self.system = system
        self.example_assistant = example_assistant
        self.text_input = text_input
        self._messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": self.example_user},
            {"role": "assistant", "content": self.example_assistant},
            {"role": "user", "content": self.text_input},
        ]
        self._index = 0  # Initialize index for the iterator

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._messages):
            result = self._messages[self._index]
            self._index += 1
            return result
        else:
            self._index = 0  # Reset the index in case you want to iterate again
            raise StopIteration  # Signal that iteration is complete

    # Convert Message object to an iterable message list
    def as_message_list(self):
        return self._messages

    def insert_text_into_message(self, attribute_name, insert_str: str, position):
        """
        Inserts the content of a text file into one of the object's string attributes at a specified position.

        Parameters:
            self: The instance of the Messages class.
            insert_str (str): The string to insert at the specified position of the specified string attribute.
            attribute_name (str): The name of the attribute you want to modify (e.g., "example_user_prompt").
            position (int): The position at which to insert the text in the selected attribute.

        Returns:
            None: Modifies the object's internal attributes.
        """

        # Verify that the attribute exists
        if not hasattr(self, attribute_name):
            print(f"The object has no attribute named '{attribute_name}'.")
            return

        # Get old content
        old_content = getattr(self, attribute_name)

        # Check if old_content is a string
        if not isinstance(old_content, str):
            print(f"The attribute '{attribute_name}' is not a string.")
            return

        # Insert new content
        if position == -1:
            new_content = old_content + insert_str
        else:
            new_content = old_content[:position] + insert_str + old_content[position:]

        # Update the attribute
        setattr(self, attribute_name, new_content)






