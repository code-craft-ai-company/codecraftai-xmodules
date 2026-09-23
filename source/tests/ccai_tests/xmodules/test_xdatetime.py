
import unittest
import time

from datetime import datetime

from ccai.xmodules.xdatetime import (
    current_time_millis,
    format_datetime_with_fractional,
    format_time_with_fractional,
    parse_datetime
)

class TestXDatetime(unittest.TestCase):

    def test_current_time_millis(self):
        now = time.time() * 1000
        ct = current_time_millis()
        self.assertLess(abs(ct - now), 1000)

    def test_format_and_parse_datetime(self):
        now_dt = datetime.now()
        fstr = format_datetime_with_fractional(now_dt)
        parsed = parse_datetime(fstr)
        self.assertEqual(parsed, now_dt.replace(microsecond=parsed.microsecond))

    def test_format_time_with_fractional(self):
        ts = time.time()
        fstr = format_time_with_fractional(ts)
        dt = parse_datetime(fstr)
        self.assertAlmostEqual(dt.timestamp(), ts, delta=1)

if __name__ == '__main__':
    unittest.main()
