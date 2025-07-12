import unittest

from automojo.errors.exceptions import LooperError
from automojo.xmodules.xthreading.looperqueue import LooperQueue, LooperQueueShutdown


class TestLooperQueue(unittest.TestCase):
    def test_push_and_pop_single(self):
        queue = LooperQueue()
        queue.push_work('a')
        self.assertEqual(queue.pop(), 'a')

    def test_push_work_packets_returns_count(self):
        queue = LooperQueue()
        available = queue.push_work_packets(['x', 'y'])
        # Only one semaphore release occurs, so only the first item can be popped
        self.assertEqual(available, 2)
        self.assertEqual(queue.pop(), 'x')

    def test_push_after_shutdown_raises(self):
        queue = LooperQueue()
        queue.shutdown_and_wait(1)
        with self.assertRaises(LooperError):
            queue.push_work('late')


if __name__ == '__main__':
    unittest.main()
