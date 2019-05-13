"""Utility functions for stationarizer."""

import logging


LOGGER = logging.getLogger("stationarizer")


def set_verbosity_level(verbosity_level):
    """Sets stationarizer verbosity level to the given number.

    Parameters
    ----------
    verbosity_level : int, logging.Logger
        The verbosity level. If an integer is given, it is set as the level of
        the default logging.Logger object. If a logging.Logger object is given,
        it is used for logging instead.
    """
    global LOGGER
    if isinstance(verbosity_level, int):
        prev = LOGGER.getEffectiveLevel()
        LOGGER.setLevel(verbosity_level)
        return prev
    elif isinstance(verbosity_level, logging.Logger):
        LOGGER = verbosity_level
        return verbosity_level
    else:
        raise TypeError((
            "Valid types for the verbosity argument are int and logging.Logger"
            " only!"))


def get_logger():
    return LOGGER
