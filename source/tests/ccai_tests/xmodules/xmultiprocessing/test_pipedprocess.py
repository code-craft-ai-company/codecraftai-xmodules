import io
import sys
import time
import unittest

from ccai.xmodules.xmuliprocessing.pipedprocess import PipedProcess


def child_func():
    print("child_out")
    print("child_err", file=sys.stderr)


class TestPipedProcess(unittest.TestCase):

    def test_capture_stdout_stderr(self):
        orig_out = sys.stdout
        orig_err = sys.stderr
        real_out = sys.__stdout__
        real_err = sys.__stderr__
        out_capture = io.StringIO()
        err_capture = io.StringIO()
        sys.stdout = out_capture
        sys.stderr = err_capture
        sys.__stdout__ = out_capture
        sys.__stderr__ = err_capture
        try:
            proc = PipedProcess(target=child_func)
            proc.start()
            proc.join()
            time.sleep(0.2)
        finally:
            sys.stdout = orig_out
            sys.stderr = orig_err
            sys.__stdout__ = real_out
            sys.__stderr__ = real_err
        self.assertIn("child_out", out_capture.getvalue())
        self.assertIn("child_err", err_capture.getvalue())


if __name__ == '__main__':
    unittest.main()
