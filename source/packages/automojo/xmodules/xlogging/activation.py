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


from typing import Optional, Union

import logging
import os
import sys

from automojo.errors.exceptions import SemanticError
from automojo.xmodules.xfspath import expand_path

ACTIVATING_PROCESS = None
ACTIVATED_MODE = None


class LoggingLocation:

    def __init__(self, directory: str, basename: str, ext: Optional[str] = ".log"):
        self.directory = directory
        self.basename = basename
        self.ext = ext
        return


class ACTIVATION_MODE:
    SERVICE = "service"
    INTERACTIVE = "interactive"
    COMMANDLINE = "commandline"


def activate_service_logging(console_level:Union[str, int] = logging.ERROR, file_level: Union[str, int]=logging.DEBUG, location: LoggingLocation=None):
    """
        Activates logging for a services.  This means the logging will be to a rotational log.

        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param location: Optional. Location of where to write log information.
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
    """

    return


def activate_interactive_console_logging(log_level: Union[str, int]=logging.INFO, location: LoggingLocation=None, remote_id: Optional[str] = None):
    """
        Activates logging but excludes log entries from being written to 'sys.stdout' and 'sys.stderr'.  This enables
        an interactive console experience without logging interrupting user input/output.
    
        :param log_level: The log level to set for the logger (default: INFO).
        :param location: Optional. Location of where to write log information.
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
    """

    global ACTIVATED_MODE
    global ACTIVATING_PROCESS

    current_pid = os.getpid()

    if ACTIVATING_PROCESS is not None:
        if remote_id is None:
            errmsg = f"Logging must be activated with a 'remote_id' parameter from child processes."
            raise SemanticError(errmsg)

        if ACTIVATED_MODE is not None and ACTIVATING_PROCESS == current_pid:
            errmsg = f"Logging has already been activated for mode {ACTIVATED_MODE} by process id={ACTIVATING_PROCESS}."
            raise SemanticError(errmsg)
        
        if ACTIVATED_MODE != ACTIVATION_MODE.INTERACTIVE:
            errmsg = f"Logging was already activated for mode={ACTIVATED_MODE}, you cannot change the logging mode."
            raise SemanticError(errmsg)
    else:
        ACTIVATING_PROCESS =  current_pid
    

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


def activate_commandline_logging(console_level:Union[str, int] = logging.ERROR, file_level: Union[str, int]=logging.DEBUG, location: LoggingLocation=None):
    """
        Activates logging for commandline tools and commands where the user wants keep the log output to the console less verbose but still
        capture more detailed logs in a file.
    
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param location: Optional. Location of where to write log information.
        :param remote_id: Optional identifier that can be passed when a remote process or remote host and process are logging outside the main context.
    """



    return
