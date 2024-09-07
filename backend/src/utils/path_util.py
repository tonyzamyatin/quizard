"""
This file contains utility functions for handling file paths inside the project

It assumes that this file is located at `backend/src/utils`.
"""

from pathlib import Path

from src.enums.generatorOptions import SupportedLanguage, GeneratorMode


def get_project_root() -> Path:
    """Return path to repository root"""
    return Path(__file__).resolve().parent.parent.parent


def get_src_root() -> Path:
    """Return path to src root"""
    return get_project_root() / 'src'


def get_config_dir() -> Path:
    """Return path to config directory"""
    return get_src_root() / 'config'


def get_assets_dir() -> Path:
    """Return path to asset directory"""
    return get_project_root() / 'assets'


def get_logs_dir() -> Path:
    """Return path to logs directory"""
    return get_project_root() / 'logs'


def get_prompts_dir() -> Path:
    """Return path to prompts directory"""
    return get_assets_dir() / 'prompts'


def get_system_prompt_path(generator_mode: GeneratorMode, lang: SupportedLanguage):
    return get_prompts_dir() / 'system' / generator_mode.lower() / f"{lang.lower()}.txt"


def get_example_prompt_path(name: str, example_type: str, lang: SupportedLanguage):
    return get_prompts_dir() / 'example' / name / example_type / f"{lang.lower()}.txt"


def get_additional_prompt_path(name: str, lang: SupportedLanguage):
    return get_prompts_dir() / 'additional' / name / f"{lang.lower()}.txt"


if __name__ == "__main__":
    print(get_project_root())
