"""
.. module:: xpath
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains additional helper functions for working with filesystem paths.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os

DEFAULT_PATH_EXPANSIONS = [
    os.path.expanduser,
    os.path.expandvars,
    os.path.abspath
]

def expand_path(path_in: str, expansions=DEFAULT_PATH_EXPANSIONS) -> str:
    """
        Applies a sequence of expansion functions to ``path_in``.

        :param path_in: Path string to expand.
        :param expansions: Iterable of callables used to transform the path.

        :returns: The fully expanded path string.
    """
    path_out = path_in
    for expansion_func in expansions:
        path_out = expansion_func(path_out)

    return path_out