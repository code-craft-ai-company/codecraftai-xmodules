import os
import io
import unittest

from multiprocessing import Queue

from automojo.xmodules.xmuliprocessing.remotestdtee import RemoteStdTee


class TestRemoteStdTee(unittest.TestCase):

    def test_write_emits_on_newline(self):
        q = Queue()
        orig = io.StringIO()
        tee = RemoteStdTee(q, orig)
        tee.write("hello")
        self.assertTrue(q.empty())
        tee.write(os.linesep)
        msg = q.get(timeout=1)
        self.assertIn("hello", msg)
        self.assertEqual(orig.getvalue(), "hello" + os.linesep)

    def test_flush_emits_buffer(self):
        q = Queue()
        orig = io.StringIO()
        tee = RemoteStdTee(q, orig)
        tee.write("abc")
        tee.flush()
        msg = q.get(timeout=1)
        self.assertIn("abc", msg)
        self.assertEqual(orig.getvalue(), "abc")


if __name__ == '__main__':
    unittest.main()
