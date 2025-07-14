
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import logging
import os
import sys


from automojo.xmodules.xlogging.levels import LogLevel


LOGGING_SECTION_MARKER = "="
LOGGING_SECTION_MARKER_LENGTH = 80


class SWAPPABLE_HOOKS:
    # We capture references to sys.stdout and sys.stderr here so we can
    # swap out the file descriptor used by logging for testing purposes
    HOOK_SYS_STDOUT = None
    HOOK_SYS_STDERR = None


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


def use_enhanced_logger():
    """
        Swap out the default logger for the 'logging' module so we can add additional enhanced logging methods and behaviors.
        
        ..note: Calling this method in order to swap out the default logger class ensures that we capture references to the stdout
        and stdin files if we want.  This also allows us to swap out the stdin and stdout references the logger uses which allows
        us to capture the output that would have been written to stdout and standard in for debugging.
    """

    # Capture stdout and stderr so the enhanced logger can force a write to the std output when
    # a call to the 'render' method is made
    SWAPPABLE_HOOKS.HOOK_SYS_STDOUT = sys.stdout
    SWAPPABLE_HOOKS.HOOK_SYS_STDERR = sys.stderr

    logging.setLoggerClass(EnhancedLogger)

    return


class EnhancedLogger(logging.Logger):

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


class EnhancedRootLogger(EnhancedLogger):
    """
    A root logger is not that different to any other logger, except that
    it must have a logging level and there is only one instance of it in
    the hierarchy.
    """
    def __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        EnhancedLogger.__init__(self, "root", level)

    def __reduce__(self):
        return logging.getLogger, ()
    
    def adopt_children(self, other_root: logging.RootLogger):

        # Tell all of the root loggers children that we are the new parent
        children_of_root = [c for c in other_root.manager.loggerDict.values()]
        for child in children_of_root:
            if hasattr(child, "parent") and child.parent is other_root:
                child.parent = self

        return

