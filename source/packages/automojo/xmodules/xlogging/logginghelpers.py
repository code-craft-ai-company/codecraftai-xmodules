
from typing import Union

import logging


def loglevel_as_int(level: Union[str, int]) -> int:
    """Guarnatees that a logging level is a numerical level."""

    numerical_level = level
    if isinstance(level, str):
        level_mapping = logging.getLevelNamesMapping()
        numerical_level = level_mapping[level]

    return numerical_level

def loglevel_as_name(level: Union[str, int]) -> str:
    """Guarnatees that a logging level is a level namer."""

    level_name = level
    if isinstance(level, int):
        level_name = logging.getLevelName(level)

    return level_name