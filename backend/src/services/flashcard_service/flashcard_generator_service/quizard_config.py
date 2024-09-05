import os
from enum import Enum

import structlog

from src.utils.path_util import get_config_dir
from src.custom_exceptions.internal_exceptions import ConfigInvalidValueError, ConfigFieldNotFoundError
from src.utils.file_util import load_yaml_config
from src.utils.env_util import get_env_variable

config_dir = get_config_dir()
logger = structlog.getLogger(__name__)


class QuizardConfig:
    _config = load_yaml_config(config_dir, get_env_variable("QUIZARD_CONFIG"))
    _model_config = None
    _token_limits = None
    _text_splitting_config = None
    _prompt_config = None

    @classmethod
    def get_config(cls):
        if cls._config is None:
            cls._config = load_yaml_config(config_dir, get_env_variable("QUIZARD_CONFIG"))
        return cls._config

    @classmethod
    def get_model_config(cls) -> dict:
        if cls._model_config is None:
            cls._model_config = cls.get_config().get('model')
            cls.validate_model_config(cls._model_config)
        return cls._model_config

    @classmethod
    def get_token_limits(cls) -> dict:
        if cls._token_limits is None:
            cls._token_limits = cls.get_config().get('token_limits')
            cls.validate_token_limits(cls._token_limits)
        return cls._token_limits

    @classmethod
    def get_text_splitting_config(cls) -> dict:
        if cls._text_splitting_config is None:
            cls._text_splitting_config = cls.get_config().get('text_splitting')
        return cls._text_splitting_config

    @classmethod
    def get_prompt_config(cls) -> dict:
        if cls._prompt_config is None:
            cls._prompt_config = cls.get_config().get('prompts')
        return cls._prompt_config

    @staticmethod
    def validate_model_config(config: dict) -> None:
        validate_field(config, 'model_name', str)
        validate_field(config, 'temperature', float, 0.0, 1.0)
        validate_field(config, 'top_p', float, 0.0, 1.0)
        validate_field(config, 'frequency_penalty', float, 0.0, 1.0)
        validate_field(config, 'presence_penalty', float, 0.0, 1.0)
        if config['model_name'] not in SupporterModels.__members__.values():
            raise ConfigInvalidValueError("Invalid model name")

    @staticmethod
    def validate_token_limits(config: dict) -> None:
        validate_field(config, 'app_limit', int, 0)
        validate_field(config, 'prompt_limit', int, 0)
        validate_field(config, 'completion_limit', int, 0)
        if config['app_limit'] - (config['prompt_limit'] + config['completion_limit']) <= 0:
            raise ConfigInvalidValueError("The sum of the prompts token and the completion token limits exceeds the total token limit of the app.")

    @staticmethod
    def validate_text_splitting_config(config: dict) -> None:
        validate_field(config, 'overlap_type', str)
        validate_field(config, 'relative_overlap', float, 0.0, 1.0)
        validate_field(config, 'absolute_overlap', int, 0)
        if config['overlap_type'] not in ['relative', 'absolute']:
            raise ConfigInvalidValueError("Invalid overlap type")

    @staticmethod
    def validate_prompt_config(config: dict) -> None:
        validate_field(config, 'example_prompt', str)
        validate_field(config, 'additional_prompt', str)


class SupporterModels(str, Enum):
    """
    Enum class for supported OpenAI models.
    """
    gpt3 = "gpt-3.5-turbo"
    gpt3_0125 = "gpt-3.5-turbo-0125"


def validate_field(config: dict, field: str, expected_type: type, min_value=None, max_value=None) -> None:
    if field not in config:
        raise ConfigFieldNotFoundError(f"Missing field in config: {field}")
    if not isinstance(config[field], expected_type):
        raise ConfigInvalidValueError(f"Invalid type for field {field}: Expected {expected_type}, got {type(config[field])}")
    if isinstance(expected_type, (int, float)):
        if min_value is not None and config[field] < min_value:
            raise ConfigInvalidValueError(f"Invalid value for field {field}: Must be >= {min_value}")
        if max_value is not None and config[field] > max_value:
            raise ConfigInvalidValueError(f"Invalid value for field {field}: Must be <= {max_value}")
