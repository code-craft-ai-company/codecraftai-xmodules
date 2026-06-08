import unittest
import time

from ccai.errors.exceptions import LooperError
from ccai.xmodules.xthreading.looper import Looper
from ccai.xmodules.xthreading.looperqueue import LooperQueueShutdown
from ccai.xmodules.xthreading.looperpool import LooperPool


class DummyLooper(Looper):
    def __init__(self, queue, processed, **kwargs):
        super().__init__(queue, **kwargs)
        self.processed = processed

    def loop(self, packet):
        self.processed.append(packet)

    def join(self):
        self._thread.join()


class TestLooperPool(unittest.TestCase):
    def _stop_pool(self, pool):
        pool._running = False
        for _ in pool._threads:
            pool._queue.push_work(LooperQueueShutdown())
        for looper in pool._threads:
            looper.join()

    def test_pool_starts_and_scales(self):
        processed = []
        pool = LooperPool(DummyLooper, group_name='grp', min_loopers=1, max_loopers=2,
                          highwater=1, daemon=True, processed=processed)
        pool.start_pool()
        time.sleep(0.1)
        self.assertEqual(len(pool._threads), 1)
        pool.push_work('one')
        pool.push_work('two')
        while len(processed) < 2:
            time.sleep(0.05)
        self.assertEqual(set(processed), {'one', 'two'})
        self.assertEqual(len(pool._threads), 2)
        self._stop_pool(pool)

    def test_start_twice_and_push_after_stop(self):
        processed = []
        pool = LooperPool(DummyLooper, group_name='grp', min_loopers=1, max_loopers=1,
                          highwater=1, daemon=True, processed=processed)
        pool.start_pool()
        with self.assertRaises(LooperError):
            pool.start_pool()
        self._stop_pool(pool)
        with self.assertRaises(LooperError):
            pool.push_work('late')


if __name__ == '__main__':
    unittest.main()
