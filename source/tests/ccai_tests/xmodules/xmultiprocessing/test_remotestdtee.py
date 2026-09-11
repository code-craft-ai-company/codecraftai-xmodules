"""
    Tests for :class:`ccai.xmodules.xmuliprocessing.remotestdtee.RemoteStdTee`.

    The tee sits in front of Python's text layer, where the line terminator is
    always '\\n' regardless of platform, so the tests write '\\n' rather than
    ``os.linesep``.
"""

import io
import os
import queue
import unittest

from multiprocessing import Queue

from ccai.xmodules.xmuliprocessing.remotestdtee import RemoteStdTee


QUEUE_GET_TIMEOUT = 5


class TestRemoteStdTee(unittest.TestCase):

    def setUp(self) -> None:
        self.queue = Queue()
        self.orig = io.StringIO()
        self.tee = RemoteStdTee(self.queue, self.orig)
        return

    def tearDown(self) -> None:
        # Retire the queue feeder thread now rather than at interpreter exit.
        self.queue.close()
        self.queue.join_thread()
        return

    def _assert_queue_stays_empty(self) -> None:
        with self.assertRaises(queue.Empty):
            self.queue.get(timeout=0.2)
        return

    def test_write_without_newline_is_buffered(self) -> None:
        self.tee.write("hello")
        self._assert_queue_stays_empty()
        return

    def test_write_always_reaches_original_file(self) -> None:
        self.tee.write("hello")
        self.assertEqual(self.orig.getvalue(), "hello")
        return

    def test_newline_emits_buffered_line(self) -> None:
        self.tee.write("hello")
        self.tee.write("\n")
        msg = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertIn("hello", msg)
        return

    def test_print_style_newline_is_recognised_on_every_platform(self) -> None:
        # print() writes '\n' even on Windows, where os.linesep is '\r\n'.
        self.tee.write("hello\n")
        msg = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertIn("hello", msg)
        return

    def test_emitted_line_is_tagged_with_pid(self) -> None:
        self.tee.write("hello\n")
        msg = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertTrue(msg.startswith(f"[{os.getpid()}] "))
        return

    def test_text_after_last_newline_is_retained(self) -> None:
        self.tee.write("first\nsecond")
        msg = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertIn("first", msg)
        self.assertNotIn("second", msg)
        self.assertEqual(self.tee.getvalue(), "second")
        return

    def test_flush_emits_buffer(self) -> None:
        self.tee.write("abc")
        self.tee.flush()
        msg = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertIn("abc", msg)
        return

    def test_flush_clears_buffer(self) -> None:
        self.tee.write("abc")
        self.tee.flush()
        self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.assertEqual(self.tee.getvalue(), "")
        return

    def test_second_flush_emits_nothing(self) -> None:
        self.tee.write("abc")
        self.tee.flush()
        self.queue.get(timeout=QUEUE_GET_TIMEOUT)
        self.tee.flush()
        self._assert_queue_stays_empty()
        return


if __name__ == '__main__':
    unittest.main()
