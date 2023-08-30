class Messages:
    def __init__(self, example_user_prompt: str, example_system_prompt: str, example_response: str,
                 input_system_prompt: str, input_user_prompt):
        self.example_user_prompt = example_user_prompt
        self.example_system_prompt = example_system_prompt
        self.example_response = example_response
        self.input_system_prompt = input_system_prompt
        self.input_user_prompt = input_user_prompt

    # create a method to convert to messages
    def as_message_list(self):
        return [{"role": "system", "content": self.example_system_prompt},
                {"role": "user", "content": self.example_user_prompt},
                {"role": "assistant", "content": self.example_response},
                {"role": "system", "content": self.input_system_prompt},
                {"role": "user", "content": self.input_user_prompt}
                ]

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






