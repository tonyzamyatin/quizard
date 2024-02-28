import json

import pytest
from openai import OpenAI

from src.flashcard_service.completion_messages.completion_messages import Messages
from src.flashcard_service.flashcard.flashcard import Flashcard, FlashcardType
from src.flashcard_service.flashcard_deck.flashcard_deck import FlashcardDeck
from src.flashcard_service.flashcard_generator.flashcard_generator import FlashcardGenerator


# test_flashcard.py

class TestFlashcard:
    """Class for testing the Flashcard class."""

    @pytest.fixture
    def sample_flashcard(self):
        """Fixture to create a Flashcard object for testing."""
        return Flashcard(1, FlashcardType.DEFINITION, "What is pytest?", "A testing framework for Python.")

    def test_flashcard_creation(self, sample_flashcard):
        """Test the Flashcard object creation with valid attributes."""
        assert sample_flashcard.id == 1
        assert sample_flashcard.type == FlashcardType.DEFINITION
        assert sample_flashcard.front_side == "What is pytest?"
        assert sample_flashcard.back_side == "A testing framework for Python."

    def test_flashcard_str(self, sample_flashcard):
        """Test the string representation of the Flashcard object."""
        expected_str = ("[DEFINITION]\n"
                        "Front side: What is pytest?\n"
                        "Back side: A testing framework for Python.\n")
        assert str(sample_flashcard) == expected_str

    def test_flashcard_as_csv(self, sample_flashcard):
        """Test the CSV format representation of the Flashcard object."""
        expected_csv = "What is pytest?;A testing framework for Python."
        assert sample_flashcard.as_csv() == expected_csv


class TestFlashcardDeck:
    @pytest.fixture
    def sample_flashcards(self):
        return [
            Flashcard(1, FlashcardType.DEFINITION, "Front1", "Back1"),
            Flashcard(2, FlashcardType.MULTIPLE_CHOICE, "Front2", "Back2")
        ]

    @pytest.fixture
    def flashcard_deck(self, sample_flashcards):
        return FlashcardDeck(sample_flashcards)

    def test_init(self, flashcard_deck, sample_flashcards):
        assert flashcard_deck.flashcards == sample_flashcards

    def test_to_json(self, flashcard_deck):
        # Convert to JSON and back, then compare
        json_data = flashcard_deck.to_json()
        data = json.loads(json_data)
        assert data == {"flashcards": [vars(card) for card in flashcard_deck.flashcards]}

    def test_to_dict_list(self, flashcard_deck):
        dict_list = flashcard_deck.to_dict_list()
        expected_list = [{'id': card.id, 'type': card.type.name,
                          'frontSide': card.front_side, 'backSide': card.back_side}
                         for card in flashcard_deck.flashcards]
        assert dict_list == expected_list

    def test_save_as_csv(self, flashcard_deck, tmp_path):
        file_path = tmp_path / "test_deck.csv"
        flashcard_deck.save_as_csv(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            expected_content = '\n'.join([card.as_csv() for card in flashcard_deck.flashcards])
            assert content == expected_content


class TestFlashcardGenerator:

    @pytest.fixture
    def generator(self, mocker):
        # Setup generator with a mock client

        # Create a mock OpenAI client
        mock_client = mocker.MagicMock(spec=OpenAI)
        # Set up the return_value for the create method
        mock_client.chat.completions.create.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": """
                            [Concept] Q1; A1
                            [Critical Thinking] Q2; A2
                            [Term] Q3; A3
                        """
                    }
                }
            ]
        }

        model_config = {
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        generator = FlashcardGenerator(client=mock_client, model_config=model_config, generation_mode='practice')
        return generator

    def test_generate_flashcards_success(self, mocker, generator):

        # Create mock Messages object
        mock_messages = mocker.MagicMock(spec=Messages)
        mock_messages.as_message_list.return_value = [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "example user prompt"},
            {"role": "assistant", "content": "example assistant response"},
            {"role": "user", "content": "user input text"},
        ]

        # Call the method you want to test
        flashcards = generator.generate_flashcards(
            model="test_model",
            messages=mock_messages.as_message_list,
            max_tokens=100,
            start_id=1,
            batch_number=1
        )

        # Assert that the method is called with correct parameters
        mocker.assert_called_once()
        assert mocker.call_args[1]['model'] == "test_model"
        assert mocker.call_args[1]['max_tokens'] == 100
        assert mocker.call_args[1]['start_id'] == 1
        assert mocker.call_args[1]['batch_number'] is None

        # Assert that the method returns the correct flashcards
        assert len(flashcards) == 3
        for i in range(3):
            assert flashcards[i].__class__ == Flashcard.__class__
            assert flashcards[i].id == i
            assert flashcards[i].front_side == f"Q{i}"
            assert flashcards[i].back_side == f"A{i}"

    # You would repeat similar tests to cover different aspects of the FlashcardGenerator class behavior
