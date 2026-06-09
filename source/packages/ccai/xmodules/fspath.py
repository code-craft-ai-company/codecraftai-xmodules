"""
.. module:: fspath
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains functions for working with file system
               paths and for working in the file system with python modules.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from types import ModuleType
from typing import List, Optional, Set, Union

import importlib
import os

TRANSLATE_TABLE_NORMALIZE_FOR_PATH = str.maketrans({
    ",": " ",
    ".": " ",
    ":": " ",
    ";": " "
})

{'/r': ' ', '/n': ' ', '/t': ' '}

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

def collect_python_modules(search_dir: str, max_depth=None) -> List[str]:
    """
        Walks a directory tree of python modules and collects the names
        of all of the python module files or .py files.  This method allows
        for python namespaces by not forcing the root folder to contain a
        __init__.py file.

        :params searchdir: The root directory to search when collecting python modules.
        :params max_depth: The maximum depth to search for python modules.  If this is None
                        then the entire directory tree will be searched.  If this is
                        an integer then the search will be limited to that depth.
        
        :returns: A list of the full paths to the python module files.
    """
    pyfiles = []

    search_dir = os.path.abspath(search_dir)
    search_dir_len = len(search_dir)

    for root, _, files in os.walk(search_dir, topdown=True):

        if max_depth is not None:
            dir_leaf = root[search_dir_len:].strip(os.path.sep)
            depth = 0
            if dir_leaf != '':
                dir_leaf_parts = dir_leaf.split(os.path.sep)
                depth = len(dir_leaf_parts)
                if depth > max_depth:
                    break

        for fname in files:
            fbase, fext = os.path.splitext(fname)
            if fext == '.py' and fbase != "__init__":
                ffull = os.path.join(root, fname)
                pyfiles.append(ffull)

    return pyfiles

def ensure_directory_is_package(package_dir: str, package_title: Optional[str] = None):
    """
        Ensures that a directory is represented to python as a package by checking to see if the
        directory has an __init__.py file and if not it adds one.

        :param package_dir: The directory to represent as a package.
        :param package_title: Optional title to be written into the documentation string in the package file.
    """
    package_dir_init = os.path.join(package_dir, "__init__.py")
    if not os.path.exists(package_dir_init):
        with open(package_dir_init, 'w') as initf:
            initf.write('"""\n')
            if package_title is not None:
                initf.write('   %s\n' % package_title)
            initf.write('"""\n')
    return

def get_directory_for_code_container(container: str) -> str:
    """
        Returns the directory for a code container (module or package)

        :param container: The code container you want to get a directory for.

        :returns: The string that represents the parent directory of the code
                  container specified.
    """
    if hasattr(container, '__path__'):
        container_dir = str(container.__path__[0]).rstrip(os.sep)
    elif hasattr(container, '__file__'):
        container_dir = os.path.dirname(container.__file__).rstrip(os.sep)
    else:
        raise RuntimeError("Unable to get parent dir for module") from None

    return container_dir

def get_module_path(module: Union[str, ModuleType]) -> str:
    """
        Returns the absolute filesystem path to a module.

        :param module: Module object or dotted import string reference to the module.

        :returns: Absolute path to the module file.

        :raises ValueError: If the provided reference resolves to a package.
    """
    module_obj = module
    if isinstance(module, str):
        module_obj = importlib.import_module(module)

    if hasattr(module_obj, "__path__"):
        raise ValueError(f"{module!r} resolves to a package; only modules are supported.") from None

    module_path = getattr(module_obj, "__file__", None)
    if module_path is None:
        raise RuntimeError(f"Unable to determine module path for {module!r}") from None

    return os.path.abspath(module_path)

def get_package_paths(package: Union[str, ModuleType]) -> List[str]:
    """
        Returns the filesystem paths associated with a package (including namespace packages).

        :param package: Package object or dotted import string reference to the package.

        :returns: List of absolute directory paths that contribute to the package.

        :raises ValueError: If the provided reference does not resolve to a package.
    """
    package_obj = package
    if isinstance(package, str):
        package_obj = importlib.import_module(package)

    package_paths = getattr(package_obj, "__path__", None)
    if package_paths is None:
        raise ValueError(f"{package!r} does not resolve to a package.") from None

    resolved_paths: List[str] = []
    seen: Set[str] = set()
    for pkg_path in package_paths:
        abs_path = os.path.abspath(pkg_path)
        if abs_path not in seen:
            resolved_paths.append(abs_path)
            seen.add(abs_path)

    return resolved_paths

def get_expanded_path(path: str) -> str:
    """
        Returns a path expanded using expanduser, expandvars and abspath for
        the provided path.

        :param path: A path which you want to expand to a full path, expanding the
                     user, variables and relative path syntax.

        :returns: The expanded path
    """
    exp_path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
    return exp_path

def normalize_name_for_path(name: str) -> str:
    """
        Normalizes a path string by replacing ",.:;" with space and then removing
        white space.

        :param name: A name as a str which is to be normalized to allow it to be used in a path.

        :returns: The normalized string which can be used in a path.
    """
    norm_name = name.translate(TRANSLATE_TABLE_NORMALIZE_FOR_PATH).replace(" ", "")
    return norm_name
