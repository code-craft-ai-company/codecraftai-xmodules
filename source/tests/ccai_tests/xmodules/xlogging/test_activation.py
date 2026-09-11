"""
    Tests for :mod:`ccai.xmodules.xlogging.activation`.

    The 'remote_id' scenarios activate logging from a child process.  The child
    is a :class:`multiprocessing.Process` with a module-level target so that it
    works under the 'spawn' start method (Windows, macOS) as well as 'fork'.
    Under 'spawn' the child does not inherit the parent's module state, so the
    target re-creates the "already activated by the parent" condition
    explicitly from the parent's pid before it activates with a remote id.
"""

import os
import shutil
import sys
import tempfile
import unittest
import logging
import multiprocessing

from logging.handlers import RotatingFileHandler

from logging import FileHandler

from ccai.xmodules.xlogging import activation
from ccai.xmodules.xlogging.parameters import LoggingLocation
from ccai.xmodules.xlogging.activation import (
    ACTIVATION_MODE,
    ActivationInfo,
    activate_service_logging,
    activate_standard_file_logging,
    activate_interactive_console_logging,
)


# Generous upper bound for a child that only activates logging; a spawned
# child has to start a fresh interpreter and import the test package first.
CHILD_JOIN_TIMEOUT = 30


def child_activates_with_remote_id(mode: ACTIVATION_MODE, parent_pid: int, directory: str, basename: str) -> None:
    """
        Child-process target: pretends logging was already activated by
        ``parent_pid`` in ``mode``, activates again with this process's pid as
        the remote id and exits 0 only if the per-remote log file was created.
    """
    activation.ACTIVATED_INFO = ActivationInfo(parent_pid, mode)

    pid = os.getpid()
    location = LoggingLocation(directory=directory, basename=basename)

    if mode == ACTIVATION_MODE.SERVICE:
        activate_service_logging(location=location, console_level=logging.INFO, file_level=logging.DEBUG,
                                 remote_id=str(pid))
    elif mode == ACTIVATION_MODE.COMMANDLINE:
        activate_standard_file_logging(location=location, console_level=logging.WARNING, file_level=logging.DEBUG,
                                       remote_id=str(pid))
    elif mode == ACTIVATION_MODE.INTERACTIVE:
        activate_interactive_console_logging(location=location, file_level=logging.INFO, remote_id=str(pid))
        clogger = logging.getLogger()
        clogger.info("Blah")
    else:
        raise ValueError(f"Unknown activation mode {mode!r}")

    expected = os.path.join(directory, f"{basename}-{pid}.log")
    if not os.path.isfile(expected):
        sys.exit(1)

    sys.exit(0)


class ActivationTestBase(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self._reset_logging()
        return

    def tearDown(self) -> None:
        self._reset_logging()
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        return

    def _reset_logging(self) -> None:
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        return

    def _run_child_activation(self, mode: ACTIVATION_MODE, basename: str) -> None:
        """
            Runs the remote-id activation in a child process, bounded by
            ``CHILD_JOIN_TIMEOUT``, and asserts that it succeeded.
        """
        parent_pid = os.getpid()
        proc = multiprocessing.Process(target=child_activates_with_remote_id,
                                       args=(mode, parent_pid, self.tmpdir, basename))
        proc.start()
        proc.join(timeout=CHILD_JOIN_TIMEOUT)

        exitcode = proc.exitcode
        if exitcode is None:
            proc.kill()
            proc.join(timeout=CHILD_JOIN_TIMEOUT)
            self.fail(f"Child activation process did not exit within {CHILD_JOIN_TIMEOUT} seconds.")

        self.assertEqual(exitcode, 0)
        return


class TestActivateServiceLogging(ActivationTestBase):

    def test_activate_service_logging(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="service")
        activate_service_logging(location=loc, console_level=logging.INFO, file_level=logging.DEBUG)

        logger = logging.getLogger()
        rfh = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        self.assertTrue(len(rfh) > 0)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "service.log")))
        return

    def test_activate_service_logging_child_remote_id(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="service")
        activate_service_logging(location=loc, console_level=logging.INFO, file_level=logging.DEBUG)

        self._run_child_activation(ACTIVATION_MODE.SERVICE, "service")
        return


class TestActivateStandardFileLogging(ActivationTestBase):

    def test_activate_standard_file_logging(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="cmd")
        activate_standard_file_logging(location=loc, console_level=logging.WARNING, file_level=logging.DEBUG)

        logger = logging.getLogger()
        fh = [h for h in logger.handlers if isinstance(h, FileHandler)]
        self.assertTrue(len(fh) > 0)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "cmd.log")))
        return

    def test_activate_standard_file_logging_child_remote_id(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="cmd")
        activate_standard_file_logging(location=loc, console_level=logging.WARNING, file_level=logging.DEBUG)

        self._run_child_activation(ACTIVATION_MODE.COMMANDLINE, "cmd")
        return


class TestActivateInteractiveConsoleLogging(ActivationTestBase):

    def test_activate_interactive_console_logging_with_file(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="int")
        activate_interactive_console_logging(location=loc, file_level=logging.INFO)

        logger = logging.getLogger()

        fh = []
        for h in logger.handlers:
            if isinstance(h, FileHandler):
                fh.append(h)

        sh = []
        for h in logger.handlers:
            if getattr(h, 'stream', None) in (sys.stdout, sys.stderr):
                sh.append(h)

        self.assertTrue(len(fh) > 0)
        self.assertEqual(len(sh), 0)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "int.log")))
        return

    def test_activate_interactive_console_logging_child_remote_id(self) -> None:
        loc = LoggingLocation(directory=self.tmpdir, basename="int")
        activate_interactive_console_logging(location=loc, file_level=logging.INFO)

        self._run_child_activation(ACTIVATION_MODE.INTERACTIVE, "int")
        return


if __name__ == '__main__':
    unittest.main()
