
"""
.. module:: xsettings
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that containing the 'ValueConverter' and 'VariableDesc' objects used for working
               with settings and environment variables.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, List, Optional, Protocol, Union

import re


ENVIRONMENT_VARIABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
INVALID_SECTION_NAME_CHARACTERS = ['[', ']', '\n', '\r', '\t', '\x00']


def assert_section_name(section_name: str) -> str:
    """
        Asserts that the section name provided is a valid configuration file section name.

        :param section_name: The section name to validate.

        :raises: AssertionError if the provided 'section_name' is not in a valid name format.
    """
    if not isinstance(section_name, str):
        errmsg = "The parameter 'section_name' must be a string."
        raise AssertionError(errmsg)

    stripped_section_name = section_name.strip()
    if len(stripped_section_name) == 0:
        errmsg = "The parameter 'section_name' must not be empty or only whitespace."
        raise AssertionError(errmsg)

    if stripped_section_name != section_name:
        errmsg = "The parameter 'section_name' must not contain leading or trailing whitespace."
        raise AssertionError(errmsg)

    for invalid_char in INVALID_SECTION_NAME_CHARACTERS:
        if invalid_char in section_name:
            errmsg = (
                f"The parameter 'section_name' contains an invalid character "
                f"'{invalid_char}'. section_name='{section_name}'"
            )
            raise AssertionError(errmsg)

    return section_name


def assert_variable_name(var_name: str) -> str:
    """
        Asserts that the variable name provided can be used as an environment variable name and
        configuration file variable name.

        :param var_name: The variable name to validate.

        :raises: AssertionError if the provided 'var_name' is not in a valid name format.
    """
    if not isinstance(var_name, str):
        errmsg = "The parameter 'var_name' must be a string."
        raise AssertionError(errmsg)

    if len(var_name) == 0:
        errmsg = "The parameter 'var_name' must not be empty."
        raise AssertionError(errmsg)

    if not ENVIRONMENT_VARIABLE_NAME_PATTERN.match(var_name):
        errmsg = (
            "The parameter 'var_name' must be a valid environment variable name and "
            "configuration file option name. Names must start with a letter or underscore and "
            "contain only alphanumeric characters or underscores."
        )
        raise AssertionError(errmsg)

    return var_name



class ValueConverter(Protocol):
    def __call__(self, string_value: str) -> Any:
        return


class VariableDesc:
    """
        Describes an application variable that is loaded from the settings file or from the environment variables
    """

    def __init__(self, *, name: str, section: str='DEFAULT', default: str=None, overrides: bool=True, context_path: Optional[str]=None):
        self._name = assert_variable_name(name)
        self._section = assert_section_name(section)
        self._default = default
        self._context_path = context_path
        self._overrides = overrides
        return
    
    @property
    def context_path(self) -> Union[str, None]:
        """
            The path that should be used to store this variable in the context.
        """
        return self._context_path

    @property
    def default(self) -> Union[str, None]:
        """
            The default value associated with this variable or None if no default was provided.
        """
        return self._default

    @property
    def name(self) -> str:
        """
            The name associated with this variable
        """
        return self._name
    
    @property
    def overrides(self) -> str:
        """
            Overrides os.environ when passed to `ThisApplication.override_variable_value`
        """
        return self._overrides

    @property
    def section(self) -> str:
        """
            The configuration file section to look for this variable in.
        """
        return self._section

    def __repr__(self):
        rval = f"AppVar(name='{self._name}', section='{self._section}')"
        return rval

    def __str__(self):
        return self._name


class VariableSet:
    """
        Class that serves as a base class for variable declaration classes. 
    """

    @classmethod
    def items(cls) -> List[VariableDesc]:
        """
            Returns the list of 'VariableDesc' class members defined on this class and any base classes.
            The variables are returned in definition order, with values on derived classes overriding
            values from base classes that share the same attribute name.
        """
        variables_by_name = {}

        for base_cls in reversed(cls.mro()):
            if base_cls is object:
                continue

            for attr_name, attr_value in base_cls.__dict__.items():
                if isinstance(attr_value, VariableDesc):
                    variables_by_name[attr_name] = attr_value

        rval: List[VariableDesc] = list(variables_by_name.values())

        return rval
