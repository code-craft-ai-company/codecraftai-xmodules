
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Dict, List, Optional, Type, Union

import logging
import logging.handlers
import os
import sys
import traceback


from automojo.xmodules.fspath import expand_path

from automojo.xmodules.xlogging.parameters import LoggingLocation, LoggingReduction
from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger
from automojo.xmodules.xlogging.recordfilters import GreaterOrEqualRecordFilter, LessThanRecordFilter
from automojo.xmodules.xlogging.swappablehooks import SWAPPABLE_HOOKS

class LoggingDefaults:
    """
        Makes all the default values associated with logging available.
    """
    DefaultFileLoggingHandler = logging.FileHandler
    DefaultRotationalLoggingHandler = logging.handlers.RotatingFileHandler

    DefaultLogfileFormat = '[%(asctime)s][%(name)s][%(levelname)s][%(message)s]'


def logging_create_branch_logger(logger_name: str, logfilename: str, log_level: Optional[Union[int, str]]=None):
    """
        Method that allows for the creation of a separate logfile for specific loggers in order
        to reduce the noise in the main logfile.  A common use for this would be to redirect
        logging from specific modules such as 'paramiko' and 'httplib' to thier own log files.
        :param logger_name: The name of the logger to create a branch log for.
    """
    root_logger = logging.getLogger()

    if logger_name in root_logger.manager.loggerDict:
        target_logger = logging.getLogger(logger_name)

        # Setup the relevant log file which will get all the
        # log entries from loggers that satisified a relevant
        # logger name prefix match
        file_handler = logging.FileHandler(logfilename)
        file_handler.setLevel(log_level)
        for hndl in list(target_logger.handlers):
            target_logger.removeHandler(hndl)
        target_logger.addHandler(file_handler)

    print("blah")

    return


def reinitialize_logging_as_interactive(location: LoggingLocation, file_level: Union[int, str], log_branches: List[Dict[str, str]] = []) -> str:
    """
        Helper method to re-initialize the logging when the path to the output directory changes shortly after startup of the framework.  This method also handles the configuration of
        output levels, stdout and stderr file wrappers.

        :param location: Location of where to write log information.
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
    """

    output_directory = expand_path(location.directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    log_ext = location.ext

    logfile_complete = os.path.join(output_directory, f"{location.basename}{log_ext}")


    # Swap out the root logger because it is set by default and if we do not swap it out, no matter
    # what we do to set the logger class the root logger will always be the normal 'Logger' derived
    # 'RootLogger'.
    root_logger: logging.RootLogger = logging.Logger.root

    root_handlers = [h for h in root_logger.handlers]
    for handler in root_handlers:
        root_logger.removeHandler(handler)

    # Set the logging level of the root logger to the logfile level, this means that all the
    # loggers will be clamped to the logging level of the root logger.
    root_logger.setLevel(file_level)


    # Setup the complete logfile
    file_handler = LoggingDefaults.DefaultFileLoggingHandler(logfile_complete)
    file_handler.setFormatter(logging.Formatter(LoggingDefaults.DefaultLogfileFormat))
    file_handler.setLevel(file_level)
    root_logger.addHandler(file_handler)

    # "DO NOT" setup stream handlers to send logging records to stdout and stderr, we are setting up
    # logging for an interactive terminal sending logging output to the terminal could be bad for the
    # user experience.

    # Do setup logging branches if any were specified.
    for binfo in log_branches:
        try:
            logger_name = binfo["name"]
            logfilename = binfo["logname"]
            log_level = binfo["loglevel"]

            logging_create_branch_logger(logger_name, logfilename, log_level)
        except Exception: # pylint: disable=broad-except
            errmsg = "Error configuration branch logger." + os.linesep
            errmsg = traceback.format_exc()
            root_logger.error(errmsg)

    # Verify our configuration by calling 'logging.getLogger()' got get the default logger
    # and use it to log that the logging as been initialized.
    elogger = getEnhancedLogger()
    elogger.section("Logging Initialized")

    return logfile_complete


def reinitialize_logging_to_standard_file(location: LoggingLocation, console_level: Union[int, str], file_level: Union[int, str],
                                          reduction: Optional[LoggingReduction] = None, log_branches: List[Dict[str, str]] = []) -> str:
    """
        Helper method to re-initialize the logging when the path to the output directory changes shortly after startup of the framework.  This method also handles the configuration of
        output levels, stdout and stderr file wrappers.

        :param location: Location of where to write log information.
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param reduction: Optional reduction parameters for creating a reduction log.
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
    """

    if SWAPPABLE_HOOKS.HOOK_SYS_STDOUT is None:
         SWAPPABLE_HOOKS.HOOK_SYS_STDOUT = sys.stdout

    if SWAPPABLE_HOOKS.HOOK_SYS_STDERR is None:
         SWAPPABLE_HOOKS.HOOK_SYS_STDERR = sys.stderr

    output_directory = expand_path(location.directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    log_ext = location.ext

    logfile_complete = None
    logfile_reduced = None

    if reduction != None:
        logfile_complete = os.path.join(output_directory, f"{reduction.swap_name}{log_ext}")
        logfile_reduced = os.path.join(output_directory, f"{location.basename}{log_ext}")
    else:
        logfile_complete = os.path.join(output_directory, f"{location.basename}{log_ext}")


    # Swap out the root logger because it is set by default and if we do not swap it out, no matter
    # what we do to set the logger class the root logger will always be the normal 'Logger' derived
    # 'RootLogger'.
    root_logger: logging.RootLogger = logging.Logger.root

    root_handlers = [h for h in root_logger.handlers]
    for handler in root_handlers:
        root_logger.removeHandler(handler)


    # Set the logging level of the root logger to the logfile level, this means that all the
    # loggers will be clamped to the logging level of the root logger.
    root_logger.setLevel(file_level)


    # Setup the complete logfile
    file_handler = LoggingDefaults.DefaultFileLoggingHandler(logfile_complete)
    file_handler.setFormatter(logging.Formatter(LoggingDefaults.DefaultLogfileFormat))
    file_handler.setLevel(file_level)
    root_logger.addHandler(file_handler)


    # Setup the reduction log file if reduction is being used.
    if logfile_reduced is not None:
        redux_handler = LoggingDefaults.DefaultFileLoggingHandler(logfile_reduced)
        redux_handler.setFormatter(logging.Formatter(LoggingDefaults.DefaultLogfileFormat))
        redux_handler.setLevel(file_level)
        root_logger.addHandler(redux_handler)


    # Setup the stdout logger with the correct console level and
    # filter the log entries from the stdout handler that are
    # greater than Info level

    stdout_handler = logging.StreamHandler(SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
    stdout_handler.setLevel(console_level)
    stdout_handler.addFilter(LessThanRecordFilter(logging.WARNING))

    stderr_handler = logging.StreamHandler(SWAPPABLE_HOOKS.HOOK_SYS_STDERR)
    stderr_handler.setLevel(console_level)
    stderr_handler.addFilter(GreaterOrEqualRecordFilter(logging.WARNING))

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)


    for binfo in log_branches:
        try:
            logger_name = binfo["name"]
            logfilename = binfo["logname"]
            log_level = binfo["loglevel"]

            logging_create_branch_logger(logger_name, logfilename, log_level)
        except Exception: # pylint: disable=broad-except
            errmsg = "Error configuration branch logger." + os.linesep
            errmsg = traceback.format_exc()
            root_logger.error(errmsg)

    # Verify our configuration by calling 'logging.getLogger()' got get the default logger
    # and use it to log that the logging as been initialized.
    elogger = getEnhancedLogger()
    elogger.section("Logging Initialized")

    return logfile_complete, logfile_reduced


def reinitialize_logging_as_service(location: LoggingLocation, console_level: Union[int, str], file_level: Union[int, str],
                                    max_bytes: int, backup_count: int, log_branches: List[Dict[str, str]] = []) -> str:
    """
        Helper method to re-initialize the logging when the path to the output directory changes shortly after startup of the framework.  This method also handles the configuration of
        output levels, stdout and stderr file wrappers.

        :param location: Location of where to write log information.
        :param console_level: The log level to set for the console output to (default: ERROR).
        :param file_level: The log level to set the file logging to (default: DEBUG)
        :param max_bytes: Maximum size in bytes of the log file before rotation occurs.
        :param backup_count: Number of rotated log files to keep.
        :param log_branches: Optional branch log specifictions for splitting specific loggers to their own logs. The spec form is {'name': '' 'logname': '', 'loglevel': ''}
    """

    if SWAPPABLE_HOOKS.HOOK_SYS_STDOUT is None:
         SWAPPABLE_HOOKS.HOOK_SYS_STDOUT = sys.stdout

    if SWAPPABLE_HOOKS.HOOK_SYS_STDERR is None:
         SWAPPABLE_HOOKS.HOOK_SYS_STDERR = sys.stderr

    output_directory = expand_path(location.directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    log_ext = location.ext


    logfile_complete = os.path.join(output_directory, f"{location.basename}{log_ext}")


    # Swap out the root logger because it is set by default and if we do not swap it out, no matter
    # what we do to set the logger class the root logger will always be the normal 'Logger' derived
    # 'RootLogger'.
    root_logger: logging.RootLogger = logging.Logger.root

    root_handlers = [h for h in root_logger.handlers]
    for handler in root_handlers:
        root_logger.removeHandler(handler)


    # Set the logging level of the root logger to the logfile level, this means that all the
    # loggers will be clamped to the logging level of the root logger.
    root_logger.setLevel(file_level)


    # Setup the complete logfile
    rotate_handler = LoggingDefaults.DefaultRotationalLoggingHandler(logfile_complete, maxBytes=max_bytes, backupCount=backup_count)
    rotate_handler.setFormatter(logging.Formatter(LoggingDefaults.DefaultLogfileFormat))
    rotate_handler.setLevel(file_level)
    root_logger.addHandler(rotate_handler)


    # Setup the stdout logger with the correct console level and
    # filter the log entries from the stdout handler that are
    # greater than Info level

    stdout_handler = logging.StreamHandler(SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
    stdout_handler.setLevel(console_level)
    stdout_handler.addFilter(LessThanRecordFilter(logging.WARNING))

    stderr_handler = logging.StreamHandler(SWAPPABLE_HOOKS.HOOK_SYS_STDERR)
    stderr_handler.setLevel(console_level)
    stderr_handler.addFilter(GreaterOrEqualRecordFilter(logging.WARNING))

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)


    for binfo in log_branches:
        try:
            logger_name = binfo["name"]
            logfilename = binfo["logname"]
            log_level = binfo["loglevel"]

            logging_create_branch_logger(logger_name, logfilename, log_level)
        except Exception: # pylint: disable=broad-except
            errmsg = "Error configuration branch logger." + os.linesep
            errmsg = traceback.format_exc()
            root_logger.error(errmsg)

    # Verify our configuration by calling 'logging.getLogger()' got get the default logger
    # and use it to log that the logging as been initialized.
    elogger = getEnhancedLogger()
    elogger.section("Logging Initialized")

    return logfile_complete
