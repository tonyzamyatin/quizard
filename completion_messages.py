class Messages:
    def __init__(self, example_user_prompt: str, example_system_prompt: str, example_response: str, input_system_prompt: str, input_user_prompt):
        self.example_user_prompt = example_user_prompt
        self.example_system_prompt = example_system_prompt
        self.example_response = example_response
        self.input_system_prompt = example_system_prompt
        self.input_user_prompt = input_user_prompt

    # create a method to convert to messages
    def as_message_list(self):
        return [{"role": "system", "content": self.example_system_prompt},
                {"role": "user", "content": self.example_user_prompt},
                {"role": "assistant", "content": self.example_response},
                {"role": "system", "content": self.input_system_prompt},
                {"role": "user", "content": self.input_user_prompt}
                ]
