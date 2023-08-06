class ExampleMessages:
    def __init__(self, example_user_input: str, example_system_prompt: str, example_response: str):
        self.example_user_input = example_user_input
        self.example_system_prompt = example_system_prompt
        self.example_response = example_response

    # create a method to convert to messages
    def as_message_list(self):
        return [{"role": "user", "content": self.example_user_input},
                {"role": "system", "content": self.example_system_prompt},
                {"role": "assistant", "content": self.example_response}]
