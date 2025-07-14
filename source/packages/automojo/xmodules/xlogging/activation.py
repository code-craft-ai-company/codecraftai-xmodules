"""
.. module:: activation
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains functions that help activate logging for different types of logging
               scenarios.
    
.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List, Optional, Union

import logging
import os
import sys

from enum import Enum

from automojo.errors.exceptions import SemanticError
from automojo.xmodules.fspath import expand_path

from automojo.xmodules.xlogging.parameters import LoggingLocation

from automojo.xmodules.xlogging.initializations import (
    reinitialize_logging_as_interactive,
    reinitialize_logging_as_service,
    reinitialize_logging_to_standard_file
)

class ACTIVATION_MODE(str, Enum):
    SERVICE = "service"
    INTERACTIVE = "interactive"
    COMMANDLINE = "commandline"

class ActivationInfo:

    def __init__(self, process_id: int, activation_mode: ACTIVATION_MODE):
        self.process_id = process_id
        self.activation_mode = activation_mode
        return


ACTIVATED_INFO: ActivationInfo = None


def activate_service_logging(location: LoggingLocation, console_level:Union[str, int] = logging.ERROR, file_level: Union[str, int]=logging.DEBUG,
                             max_bytes: int = 10 * 1024 * 1024, backup_count: int = 10, log_branches: List[Dict[str, str]] = [],
                             remote_id: Optional[str] = None):
    """
        Activates logging for a services.  This means the logging will be to a rotational log.

        :param location: Optional. Location of where to write log information.
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param max_bytes: Maximum size in bytes of the log file before rotation occurs.
        :param backup_count: Number of rotated log files to keep.
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
        
    """

    global ACTIVATED_INFO

    current_pid = os.getpid()

    if ACTIVATED_INFO is not None:
        if ACTIVATED_INFO.process_id != current_pid:
            if remote_id is None:
                errmsg = "Logging must be activated with a 'remote_id' parameter from child processes."
                raise SemanticError(errmsg)
            
            if ACTIVATED_INFO.activation_mode !=  ACTIVATION_MODE.SERVICE:
                errmsg = (f"Logging was already activated for mode={ACTIVATED_INFO.activation_mode}, "
                            "you cannot change the logging mode.")
                raise SemanticError(errmsg)
        else:
            errmsg = (f"Logging has already been activated for mode {ACTIVATED_INFO.activation_mode} "
                      f"by process id={ACTIVATED_INFO.process_id}.")
            raise SemanticError(errmsg)

    else:
        ACTIVATED_INFO = ActivationInfo(current_pid, ACTIVATION_MODE.SERVICE)

    param_location = None
    if remote_id is not None:
        param_location = LoggingLocation(location.directory, f"{location.basename}-{remote_id}", location.ext)
    else:
        param_location = location

    reinitialize_logging_as_service(param_location, console_level, file_level, max_bytes, backup_count, log_branches=log_branches)

    return


def activate_interactive_console_logging(location: LoggingLocation, file_level: Union[str, int]=logging.INFO, log_branches: List[Dict[str, str]] = [],
                                         remote_id: Optional[str] = None):
    """
        Activates logging but excludes log entries from being written to 'sys.stdout' and 'sys.stderr'.  This enables
        an interactive console experience without logging interrupting user input/output.
    
        :param location: Optional. Location of where to write log information.
        :param file_level: The log level to set for the logger (default: INFO).
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
        
    """

    global ACTIVATED_INFO

    current_pid = os.getpid()

    if ACTIVATED_INFO is not None:
        if ACTIVATED_INFO.process_id != current_pid:
            if remote_id is None:
                errmsg = "Logging must be activated with a 'remote_id' parameter from child processes."
                raise SemanticError(errmsg)
            
            if ACTIVATED_INFO.activation_mode !=  ACTIVATION_MODE.INTERACTIVE:
                errmsg = (f"Logging was already activated for mode={ACTIVATED_INFO.activation_mode}, "
                            "you cannot change the logging mode.")
                raise SemanticError(errmsg)
        else:
            errmsg = (f"Logging has already been activated for mode {ACTIVATED_INFO.activation_mode} "
                      f"by process id={ACTIVATED_INFO.process_id}.")
            raise SemanticError(errmsg)

    else:
        ACTIVATED_INFO = ActivationInfo(current_pid, ACTIVATION_MODE.INTERACTIVE)

    param_location = None
    if remote_id is not None:
        param_location = LoggingLocation(location.directory, f"{location.basename}-{remote_id}", location.ext)
    else:
        param_location = location

    reinitialize_logging_as_interactive(param_location, file_level, log_branches=log_branches)

    return


def activate_standard_file_logging(location: LoggingLocation, console_level: Union[str, int] = logging.ERROR, file_level: Union[str, int] = logging.DEBUG,
                                   log_branches: List[Dict[str, str]] = [], remote_id: Optional[str] = None):
    """
        Activates logging for commandline tools and commands where the user wants keep the log output to the console less verbose but still
        capture more detailed logs in a file.
    
        :param location: Location of where to write log information.
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.

    """
    global ACTIVATED_INFO

    current_pid = os.getpid()

    if ACTIVATED_INFO is not None:
        if ACTIVATED_INFO.process_id != current_pid:
            if remote_id is None:
                errmsg = "Logging must be activated with a 'remote_id' parameter from child processes."
                raise SemanticError(errmsg)
            
            if ACTIVATED_INFO.activation_mode !=  ACTIVATION_MODE.COMMANDLINE:
                errmsg = (f"Logging was already activated for mode={ACTIVATED_INFO.activation_mode}, "
                            "you cannot change the logging mode.")
                raise SemanticError(errmsg)
        else:
            errmsg = (f"Logging has already been activated for mode {ACTIVATED_INFO.activation_mode} "
                      f"by process id={ACTIVATED_INFO.process_id}.")
            raise SemanticError(errmsg)

    else:
        ACTIVATED_INFO = ActivationInfo(current_pid, ACTIVATION_MODE.COMMANDLINE)

    param_location = None
    if remote_id is not None:
        param_location = LoggingLocation(location.directory, f"{location.basename}-{remote_id}", location.ext)
    else:
        param_location = location

    reinitialize_logging_to_standard_file(param_location, console_level, file_level, log_branches=log_branches)

    return


