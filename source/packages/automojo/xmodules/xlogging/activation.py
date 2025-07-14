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


from typing import Dict, List, Optional, Type, Union

import logging
import logging.handlers
import os
import sys

from enum import Enum

from automojo.errors.exceptions import SemanticError
from automojo.xmodules.fspath import expand_path

from automojo.xmodules.xlogging.enhancedloggers import EnhancedRootLogger, SWAPPABLE_HOOKS
from automojo.xmodules.xlogging.recordfilters import GreaterOrEqualRecordFilter, LessThanRecordFilter

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


def activate_service_logging(console_level:Union[str, int] = logging.ERROR, file_level: Union[str, int]=logging.DEBUG,
                             location: LoggingLocation=None, remote_id: Optional[str] = None,
                             max_bytes: int = 10 * 1024 * 1024, backup_count: int = 10):
    """
        Activates logging for a services.  This means the logging will be to a rotational log.

        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param location: Optional. Location of where to write log information.
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
        :param max_bytes: Maximum size in bytes of the log file before rotation occurs.
        :param backup_count: Number of rotated log files to keep.
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

    logger = logging.getLogger()
    logger.setLevel(min(console_level, file_level))

    # Remove any existing handlers so we have a clean slate
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configure console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Configure rotating file handler if a location is specified
    if location:
        log_dir = expand_path(location.directory)
        os.makedirs(log_dir, exist_ok=True)

        log_basename = location.basename
        if remote_id is not None:
            log_basename = f"{log_basename}-{remote_id}"
        log_file = os.path.join(log_dir, f"{log_basename}{location.ext}")

        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        logger.addHandler(logging.NullHandler())

    return


def activate_interactive_console_logging(log_level: Union[str, int]=logging.INFO, location: LoggingLocation=None, remote_id: Optional[str] = None):
    """
        Activates logging but excludes log entries from being written to 'sys.stdout' and 'sys.stderr'.  This enables
        an interactive console experience without logging interrupting user input/output.
    
        :param log_level: The log level to set for the logger (default: INFO).
        :param location: Optional. Location of where to write log information.
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
    

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove handlers that write to stdout or stderr
    for handler in logger.handlers[:]:
        if getattr(handler, 'stream', None) in (None, sys.stdout, sys.stderr):
            logger.removeHandler(handler)

    # If log_file is specified, log to file; else, do not add any stream handler.
    if location:
        log_dir = expand_path(location.directory)
        log_basename = location.basename
        if remote_id is not None:
            log_basename = f"{log_basename}-{remote_id}"
        log_file = os.path.join(log_dir, f"{log_basename}{location.ext}")
                                
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Optionally, you could add a NullHandler if you want logging calls to silently do nothing
    elif not logger.handlers:
        logger.addHandler(logging.NullHandler())

    return


def activate_commandline_logging(console_level: Union[str, int] = logging.ERROR, file_level: Union[str, int] = logging.DEBUG,
                                 location: LoggingLocation = None, remote_id: Optional[str] = None):
    """
        Activates logging for commandline tools and commands where the user wants keep the log output to the console less verbose but still
        capture more detailed logs in a file.
    
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param location: Optional. Location of where to write log information.
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

    logger = logging.getLogger()
    logger.setLevel(min(console_level, file_level))

    # Remove any existing handlers so we start clean
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configure console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Configure file handler if a location is specified
    if location:
        log_dir = expand_path(location.directory)
        os.makedirs(log_dir, exist_ok=True)

        log_basename = location.basename
        if remote_id is not None:
            log_basename = f"{log_basename}-{remote_id}"
        log_file = os.path.join(log_dir, f"{log_basename}{location.ext}")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        logger.addHandler(logging.NullHandler())

    return


