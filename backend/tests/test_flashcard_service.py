import json

import pytest
from openai import OpenAI

from src.custom_exceptions.quizard_exceptions import FlashcardInvalidFormatError, FlashcardPrefixError
from src.flashcard_service.completion_messages.completion_messages import Messages
from src.flashcard_service.flashcard.flashcard import Flashcard, FlashcardType
from src.flashcard_service.flashcard_deck.flashcard_deck import FlashcardDeck
from src.flashcard_service.flashcard_generator.flashcard_generator import FlashcardGenerator, parse_flashcard, parse_flashcards


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
        # Create a generator with a mock OpenAI client and a mock config
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

    @pytest.fixture
    def messages(self, mocker):
        # Create mock Messages object
        mock_messages = mocker.MagicMock(spec=Messages)
        mock_messages.as_message_list.return_value = [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "example user prompt"},
            {"role": "assistant", "content": "example assistant response"},
            {"role": "user", "content": "user input text"},
        ]
        return mock_messages

    def test_parse_flashcard_valid_input(self):
        """Test whether valid input is parsed correctly into a single flashcard"""
        input_1 = "[Concept] Q1; A1"
        input_2 = "[Critical Thinking] Q2; A2"
        input_3 = "[Term] Q3; A3"

        flashcard_1 = parse_flashcard(id=1, line=input_1)
        flashcard_2 = parse_flashcard(id=2, line=input_2)
        flashcard_3 = parse_flashcard(id=3, line=input_3)

        assert flashcard_1 == Flashcard(1, FlashcardType.OPEN_ENDED, "Q1", "A1")
        assert flashcard_2 == Flashcard(2, FlashcardType.OPEN_ENDED, "Q2", "A2")
        assert flashcard_3 == Flashcard(3, FlashcardType.DEFINITION, "Q3", "A3")

    def test_parse_flashcard_without_delimiter(self):
        """Test whether input without delimiter raises an error as expected"""
        with pytest.raises(FlashcardInvalidFormatError):
            input_1 = "[Concept] Q1 A1"
            flashcard_1 = parse_flashcard(id=1, line=input_1)

    @pytest.mark.parametrize("input_id, input_line, expected_exception", [
        (1, "[Concept Q1; A1", FlashcardInvalidFormatError),
        (2, "Concept] Q2; A2", FlashcardInvalidFormatError),
        (3, "Concept Q3; A3", FlashcardInvalidFormatError),
        (4, "[] Q4; A4", FlashcardInvalidFormatError),
        (5, "[Something invalid] Q5; A5", FlashcardPrefixError)
    ])
    def test_parse_flashcard_with_invalid_prefix(self, input_id, input_line, expected_exception):
        """Test whether input with invalid prefix format raises an error as expected"""
        with pytest.raises(expected_exception):
            parse_flashcard(input_id, input_line)

    def test_parse_flashcards_valid_input(self):
        """Test whether a valid string of flashcards is parsed correctly"""
        input_1 = """
            [Concept] Q1; A1
            [Critical Thinking] Q2; A2
            [Term] Q3; A3"""
        flashcards = parse_flashcards(input_1, 'practice', 1, None)
        assert len(flashcards) == 3
        for i in range(3):
            assert flashcards[i].__class__ == Flashcard.__class__
            assert flashcards[i].id == i
            assert flashcards[i].front_side == f"Q{i}"
            assert flashcards[i].back_side == f"A{i}"

    def test_generate_flashcards_success(self, generator, messages, mocker):
        # Mock the create method in the OpenAI client within the generator
        mock_create = mocker.patch.object(generator.client.chat.completions, 'create', return_value={
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
        })
        # Call the method you want to test
        flashcards = generator.generate_flashcards(
            model="test_model",
            messages=messages,
            max_tokens=100,
            start_id=1,
            batch_number=1
        )

        # Assert that the OpenAI API mock method is called with correct parameters
        mock_create.assert_called_once_with(
            model="test_model",
            messages=messages.as_message_list(),
            max_tokens=100,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Assert that the method returns the correct flashcards
        assert len(flashcards) == 3
        for i in range(3):
            assert flashcards[i].__class__ == Flashcard.__class__
            assert flashcards[i].id == i
            assert flashcards[i].front_side == f"Q{i}"
            assert flashcards[i].back_side == f"A{i}"
