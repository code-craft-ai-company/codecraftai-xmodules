"""
.. module:: xpython
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains additional helper functions for modifying the root
               python behavior

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os
import sys

from ccai.xmodules.fspath import expand_path

def in_python_path(dir_to_check: str) -> bool:
    """
        Checks whether ``dir_to_check`` already appears in ``sys.path``.

        :param dir_to_check: Directory to search for.

        :returns: ``True`` if present in ``sys.path``.
    """
    dir_to_check = expand_path(dir_to_check).rstrip(os.sep)

    found = False

    for nxt_item in sys.path:
        nxt_item = expand_path(nxt_item.rstrip(os.sep))
        if nxt_item == dir_to_check:
            found = True
            break

    return found


def prepend_python_path(dir_to_add: str) -> None:
    """
        Inserts ``dir_to_add`` at the beginning of ``sys.path`` and updates
        ``PYTHONPATH`` so child processes inherit the change.

        :param dir_to_add: Directory path to prepend.
    """
    found = in_python_path(dir_to_add)

    if not found:
        sys.path.insert(0, dir_to_add)
        if "PYTHONPATH" in os.environ:
            os.environ["PYTHONPATH"] = dir_to_add + os.pathsep + os.environ["PYTHONPATH"]
        else:
            os.environ["PYTHONPATH"] = dir_to_add

    return

def append_python_path(dir_to_add: str) -> None:
    """
        Appends ``dir_to_add`` to ``sys.path`` and updates ``PYTHONPATH``
        for child processes.

        :param dir_to_add: Directory path to append.
    """
    found = in_python_path(dir_to_add)

    if not found:
        sys.path.append(dir_to_add)
        if "PYTHONPATH" in os.environ:
            os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"] + os.pathsep + dir_to_add
        else:
            os.environ["PYTHONPATH"] = dir_to_add

    return