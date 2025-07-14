import os
import shutil
import tempfile
import unittest
import logging
from logging.handlers import RotatingFileHandler

from logging import FileHandler, NullHandler
import sys

from automojo.xmodules.xlogging import activation
from automojo.xmodules.xlogging.parameters import LoggingLocation
from automojo.xmodules.xlogging.activation import (
    activate_service_logging,
    activate_standard_file_logging,
    activate_interactive_console_logging,
)


class TestActivateServiceLogging(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def test_activate_service_logging(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="service")
        activate_service_logging(location=loc, console_level=logging.INFO, file_level=logging.DEBUG)

        logger = logging.getLogger()
        rfh = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        self.assertTrue(rfh)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "service.log")))
        return

    def test_activate_service_logging_child_remote_id(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="service")
        activate_service_logging(location=loc, console_level=logging.INFO, file_level=logging.DEBUG)

        child_pid = os.fork()
        if child_pid == 0:
            try:
                pid = os.getpid()
                activate_service_logging(
                    console_level=logging.INFO,
                    file_level=logging.DEBUG,
                    location=loc,
                    remote_id=str(pid),
                )
                expected = os.path.join(self.tmpdir, f"service-{pid}.log")
                os._exit(0 if os.path.isfile(expected) else 1)
            except Exception:
                os._exit(1)
        else:
            _, status = os.waitpid(child_pid, 0)
            self.assertEqual(os.WEXITSTATUS(status), 0)
        return


class TestActivateStandardFileLogging(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def test_activate_standard_file_logging(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="cmd")
        activate_standard_file_logging(location=loc, console_level=logging.WARNING, file_level=logging.DEBUG)

        logger = logging.getLogger()
        fh = [h for h in logger.handlers if isinstance(h, FileHandler)]
        self.assertTrue(fh)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "cmd.log")))
        return

    def test_activate_standard_file_logging_child_remote_id(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="cmd")
        activate_standard_file_logging(location=loc, console_level=logging.WARNING, file_level=logging.DEBUG)

        child_pid = os.fork()
        if child_pid == 0:
            try:
                pid = os.getpid()
                activate_standard_file_logging(
                    console_level=logging.WARNING,
                    file_level=logging.DEBUG,
                    location=loc,
                    remote_id=str(pid),
                )
                expected = os.path.join(self.tmpdir, f"cmd-{pid}.log")
                os._exit(0 if os.path.isfile(expected) else 1)
            except Exception:
                os._exit(1)
        else:
            _, status = os.waitpid(child_pid, 0)
            self.assertEqual(os.WEXITSTATUS(status), 0)
        return

class TestActivateInteractiveConsoleLogging(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        activation.ACTIVATED_INFO = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
        return

    def test_activate_interactive_console_logging_with_file(self):
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
        
        self.assertTrue(fh)
        self.assertFalse(sh)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "int.log")))
        return

    def test_activate_interactive_console_logging_child_remote_id(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="int")
        activate_interactive_console_logging(location=loc, file_level=logging.INFO)

        child_pid = os.fork()
        if child_pid == 0:
            try:
                pid = os.getpid()
                activate_interactive_console_logging(
                    location=loc,
                    file_level=logging.INFO,
                    remote_id=str(pid),
                )
                expected = os.path.join(self.tmpdir, f"int-{pid}.log")
                os._exit(0 if os.path.isfile(expected) else 1)
            except Exception as xcpt:
                os._exit(1)
        else:
            _, status = os.waitpid(child_pid, 0)
            self.assertEqual(os.WEXITSTATUS(status), 0)
        return


if __name__ == '__main__':
    unittest.main()
