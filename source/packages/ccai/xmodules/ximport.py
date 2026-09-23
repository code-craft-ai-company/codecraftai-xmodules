"""
.. module:: ximport
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains functions that are utilized to support dynamic
               importing of modules based module name and directly from a file.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import sys
import importlib
import importlib.util

from types import ModuleType

NoneType = type(None)


def import_by_name(modulename: str) -> ModuleType:
    """
        Imports and returns a module by its fully qualified name.

        :param modulename: Module identifier to import.

        :returns: The loaded module object.
    """

    mod = None
    if modulename in sys.modules:
        mod = sys.modules[modulename]
    else:
        mod = importlib.import_module(modulename)

    return mod


def import_file(name: str, loc: str, by_file_only=False) -> ModuleType:
    """
        Import a module from a specific file path.

        :param name: Name assigned to the loaded module.
        :param loc: Filesystem path to the module file.
        :param by_file_only: Only attempt loading from ``loc`` if ``True``.

        :returns: The imported module.
    """
    mod = None
    if name in sys.modules:
        mod = sys.modules[name]

    if mod is None:

        while True:
            if not by_file_only:
                # First try to import the module by name only
                try:
                    mod = importlib.import_module(name)
                    break
                except ImportError:
                    # Importing by name failed; fall through and load the module from its file location below.
                    pass

            spec = importlib.util.spec_from_file_location(name, str(loc))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[name] = mod
            break

    return mod
