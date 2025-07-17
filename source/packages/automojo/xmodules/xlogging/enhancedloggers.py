
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import logging
import os
import sys
import warnings


from automojo.xmodules.xlogging.levels import LogLevel
from automojo.xmodules.xlogging.swappablehooks import SWAPPABLE_HOOKS


LOGGING_SECTION_MARKER = "="
LOGGING_SECTION_MARKER_LENGTH = 80


def format_log_section_header(title: str):
    """
        Formats a log section header by centering the title inside of the section marker character string.
    """
    title_upper = " %s " % title.strip().upper()
    marker_count = LOGGING_SECTION_MARKER_LENGTH - len(title_upper)
    marker_half = marker_count >> 1
    marker_prefix = LOGGING_SECTION_MARKER * marker_half
    marker_suffix = LOGGING_SECTION_MARKER * (marker_count - marker_half)
    header = "\n%s%s%s\n" % (marker_prefix, title_upper, marker_suffix)
    return header


class EnhancedLogger:

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        return

    def addHandler(self, hdlr):
        """
        Add the specified handler to this logger.
        """
        self._logger.addHandler(hdlr)
        return

    def callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.
        """
        self._logger.callHandlers(record)
        return

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=True)
        """
        self._logger.critical(msg, *args, **kwargs)
        return

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=True)
        """
        self._logger.debug(msg, *args, **kwargs)
        return

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=True)
        """
        self._logger.error(msg, *args, **kwargs)
        return

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        self.exception(msg, *args, exc_info=exc_info, **kwargs)
        return

    def fatal(self, msg, *args, **kwargs):
        """
        Don't use this method, use critical() instead.
        """
        self._logger.fatal(msg, *args, **kwargs)
        return

    def findCaller(self, stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        rtnitems = self._logger.findCaller(stack_info=stack_info, stacklevel=stacklevel)
        return rtnitems

    def getChild(self, suffix):
        """
        Get a logger which is a descendant to this one.

        This is a convenience method, such that

        logging.getLogger('abc').getChild('def.ghi')

        is the same as

        logging.getLogger('abc.def.ghi')

        It's useful, for example, when the parent logger is named using
        __name__ rather than a literal string.
        """
        rv = self._logger.getChild(suffix)
        return
    
    def getEffectiveLevel(self):
        """
        Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        rv = self._logger.getEffectiveLevel()
        return rv

    def handle(self, record):
        """
        Call the handlers for the specified record.

        This method is used for unpickled records received from a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        self._logger.handle(record)
        return

    def hasHandlers(self):
        """
        See if this logger has any handlers configured.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. Return True if a handler was found, else False.
        Stop searching up the hierarchy whenever a logger with the "propagate"
        attribute set to zero is found - that will be the last logger which
        is checked for the existence of handlers.
        """
        rv = self._logger.hasHandlers()
        return rv

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=True)
        """
        self._logger.info(msg, *args, **kwargs)
        return

    def isEnabledFor(self, level):
        """
        Is this logger enabled for level 'level'?
        """
        rv = self._logger.isEnabledFor(level)

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=True)
        """
        self._logger.log(level, msg, *args, **kwargs)

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = self._logger(name, level, fn, lno, msg, args, exc_info, func=func, extra=extra, sinfo=sinfo)
        return rv

    def removeHandler(self, hdlr):
        """
        Remove the specified handler from this logger.
        """
        self._logger.removeHandler(hdlr)
        return

    def render(self, line):
        """
            Logs a message to both the standard in and to the log file.
        """
        self.info(line)
        print(line, file=SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
        return

    def section(self, title):
        """
            Logs a log section marker
        """
        marker = format_log_section_header(title)

        self.log(LogLevel.NOTSET, marker)
        print(marker, file=SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
        return

    def setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        self._logger.setLevel(level)
        return

    def test_begin(self, testname, **test_args):
        """
        """
        info_msg_lines = [
            "TEST BEGIN - {}".format(testname),
            "    ARGS:"
        ]

        for arg_name, arg_value in test_args.items():

            arg_value_debug = None
            if hasattr(arg_value, "__debug_repr__"):
                arg_value_debug= arg_value.__debug_repr__()
            else:
                arg_value_debug = str(arg_value)

            info_msg_lines.append("    {} = {}".format(arg_name, arg_value_debug))

        info_msg = os.linesep.join(info_msg_lines)

        self.info(info_msg)
        print(info_msg, file=SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
        return

    def test_end(self, testname):
        info_msg = "TEST END - {}".format(testname)
        
        self.info(info_msg)
        print(info_msg, file=SWAPPABLE_HOOKS.HOOK_SYS_STDOUT)
        return

    def warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method is deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)
        return

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=True)
        """
        self._logger.warning(msg, *args, **kwargs)
        return

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        self._logger._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
        return

    def __repr__(self):
        rv = repr(self._logger)
        return rv

    def __reduce__(self):
        rv = self._logger.__reduce__()
        return rv


def getEnhancedLogger(name: str) -> EnhancedLogger:
    logger = logging.getLogger(name)
    rtnval = EnhancedLogger(logger)
    return rtnval

