import os
import shutil
import tempfile
import unittest
import logging
from logging.handlers import RotatingFileHandler

from automojo.xmodules.xlogging import activation
from automojo.xmodules.xlogging.activation import LoggingLocation, activate_service_logging


class TestActivateServiceLogging(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        activation.ACTIVATING_PROCESS = None
        activation.ACTIVATED_MODE = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        activation.ACTIVATING_PROCESS = None
        activation.ACTIVATED_MODE = None
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    def test_rotating_file_handler_added(self):
        loc = LoggingLocation(directory=self.tmpdir, basename="service")
        activate_service_logging(console_level=logging.INFO, file_level=logging.DEBUG, location=loc)

        logger = logging.getLogger()
        rfh = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        self.assertTrue(rfh)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "service.log")))


if __name__ == '__main__':
    unittest.main()
