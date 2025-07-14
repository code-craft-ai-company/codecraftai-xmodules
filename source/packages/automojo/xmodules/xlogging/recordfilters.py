
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Union

import logging


class GreaterOrEqualRecordFilter(logging.Filter):
    """
        Filters records with a log level < WARNING
    """

    def __init__(self, filter_at_level: Union[int, str]):
        super(GreaterOrEqualRecordFilter, self).__init__("GreaterOrEqualFilter")

        if isinstance(filter_at_level, str):
            level_mapping = logging.getLevelNamesMapping()
            filter_at_level = level_mapping[filter_at_level]

        self._filter_at_level = filter_at_level
        return

    def filter(self, record): # pylint: disable=no-self-use
        """
            Performs the filtering of records.
        """
        process_rec = record.levelno >= self._filter_at_level
        return process_rec


class LessThanRecordFilter(logging.Filter):
    """
        Filters records with a log level < WARNING
    """

    def __init__(self, filter_at_level: Union[int, str]):
        super(LessThanRecordFilter, self).__init__("LessThanFilter")

        if isinstance(filter_at_level, str):
            level_mapping = logging.getLevelNamesMapping()
            filter_at_level = level_mapping[filter_at_level]

        self._filter_at_level = filter_at_level
        return

    def filter(self, record): # pylint: disable=no-self-use
        """
            Performs the filtering of records.
        """
        process_rec = record.levelno < self._filter_at_level
        return process_rec

