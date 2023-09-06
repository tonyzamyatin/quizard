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

    def insert_text_into_message(self, attribute_name, insert_file_path, position):
        """
        Inserts the content of a text file into one of the object's string attributes at a specified position.

        Parameters:
            self: The instance of the Messages class.
            insert_file_path (str): The path of the text file containing the text to insert.
            attribute_name (str): The name of the attribute you want to modify (e.g., "example_user_prompt").
            position (int): The position at which to insert the text in the selected attribute.

        Returns:
            None: Modifies the object's internal attributes.
        """

        # Verify that the attribute exists
        if not hasattr(self, attribute_name):
            print(f"The object has no attribute named '{attribute_name}'.")
            return

        # Read the content of the file to insert
        with open(insert_file_path, 'r', encoding='utf-8') as file:
            insert_content = file.read()

        # Get old content
        old_content = getattr(self, attribute_name)

        # Check if old_content is a string
        if not isinstance(old_content, str):
            print(f"The attribute '{attribute_name}' is not a string.")
            return

        # Insert new content
        new_content = old_content[:position] + insert_content + old_content[position:]

        # Update the attribute
        setattr(self, attribute_name, new_content)






