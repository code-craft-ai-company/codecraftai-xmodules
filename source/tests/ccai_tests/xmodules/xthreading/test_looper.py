import unittest
import time

from ccai.xmodules.xthreading.looper import Looper
from ccai.xmodules.xthreading.looperqueue import LooperQueue, LooperQueueShutdown


class DummyLooper(Looper):
    def __init__(self, queue, processed, **kwargs):
        super().__init__(queue, **kwargs)
        self.processed = processed

    def loop(self, packet):
        self.processed.append(packet)

    def join(self):
        self._thread.join()


class TestLooper(unittest.TestCase):
    def test_looper_processes_packets_and_names(self):
        processed = []
        queue = LooperQueue()
        looper = DummyLooper(queue, processed, name='initial')
        looper.start()
        self.assertEqual(looper.thread_get_name(), 'initial')
        looper.thread_set_name('changed')
        self.assertEqual(looper.thread_get_name(), 'changed')
        queue.push_work('work')
        queue.push_work(LooperQueueShutdown())
        looper.join()
        self.assertEqual(processed, ['work'])
        self.assertFalse(looper._thread.is_alive())


if __name__ == '__main__':
    unittest.main()
