
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


from typing import Any, Callable, Dict, List, Optional, Protocol, Union

import enum
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

class VariableSource(enum.Flag):
    ENVIRONMENT = 1
    SETTINGS = 2
    BOTH = 3


class VariableDesc:
    """
        Describes an application variable that is loaded from the settings file or from the environment variables
    """

    def __init__(self, *, name: str, section: str='DEFAULT', default: str=None, overrides: bool=True, context_path: Optional[str]=None,
                 source: VariableSource=VariableSource.BOTH):
        self._name = assert_variable_name(name)
        self._section = assert_section_name(section)
        self._default = default
        self._overrides = overrides
        self._context_path = context_path
        self._source = source
    
        self._key = f"{self._section}->{self._name}"
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

    @property
    def key(self) -> str:
        """
            The key to use when storing and retrieving the variable description.
        """
        return self._key

    def __repr__(self):
        rval = f"AppVar(name='{self._name}', section='{self._section}')"
        return rval

    def __str__(self):
        return self._name


class VariableReader:
    """
        Class that establishes a way to declaratively read variables from the application variable storage.
    """

    def __init__(self, var_desc: VariableDesc, *, converter: Optional[ValueConverter] = None, conv_kwargs: Dict[str, Any]=None):
        """
            Initializes a variable reader descriptor that operates on a :class:`VariableDesc`.

            :param var_desc: The :class:`VariableDesc` describing the variable being read.
            :param converter: Optional callable used to convert string values before returning them.
        """
        if not isinstance(var_desc, VariableDesc):
            errmsg = "The parameter 'var_desc' must be an instance of VariableDesc."
            raise AssertionError(errmsg)

        self._var_desc = var_desc
        self._converter = converter
        self._conv_kwargs = conv_kwargs

        self._owner: Optional[type] = None
        return

    def __set_name__(self, owner: type, name: str) -> None:
        """
            Captures the class and attribute name this reader is bound to.
        """
        self._owner = owner

        assert_variable_name(name)
        
        if self._var_desc.name != name:
            errmsg = (
                f"VariableDesc name '{self._var_desc.name}' does not match attribute name '{name}'."
            )
            raise AssertionError(errmsg)
        
        return

    def __call__(self, instance: Optional[object], owner: Optional[type]) -> Any:
        """
            Resolves the value for this variable by delegating to :meth:`perform_read`.
        """
        target_owner = owner if owner is not None else self._owner

        resolved_value = self.perform_read(instance, target_owner)
        if resolved_value is None and self._var_desc.default is not None:
            resolved_value = self._var_desc.default

        if self._converter is not None and isinstance(resolved_value, str):
            resolved_value = self._converter(resolved_value)

        return resolved_value

    def __get__(self, instance: Optional[object], owner: Optional[type] = None) -> Any:
        """
            Supports descriptor access so referencing the attribute triggers the reader call.
        """
        return self(instance, owner)

    def perform_read(self, instance: object, owner: type, ) -> Any:
        """
            Overloadable hook used by derived classes to fetch the value for the given variable.
        """
        raise NotImplementedError("Derived classes must implement 'perform_read'")



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
