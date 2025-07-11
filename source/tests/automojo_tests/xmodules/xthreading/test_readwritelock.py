
import unittest
import threading
import time

from automojo.xmodules.xthreading.readwritelock import ReadWriteLock
from automojo.errors.exceptions import SemanticError

class TestReadWriteLock(unittest.TestCase):

    def test_readers_and_writer(self):
        lock = ReadWriteLock()
        order = []
        def reader():
            lock.acquire_read(timeout=1)
            order.append('r_acq')
            time.sleep(0.1)
            order.append('r_rel')
            lock.release_read()
        def writer():
            time.sleep(0.02)
            lock.acquire_write(timeout=1)
            order.append('w_acq')
            lock.release_write()
            order.append('w_rel')
        t1 = threading.Thread(target=reader)
        t2 = threading.Thread(target=reader)
        tw = threading.Thread(target=writer)
        t1.start(); t2.start(); tw.start()
        t1.join(); t2.join(); tw.join()
        # writer should acquire after readers released
        self.assertTrue(order.index('w_acq') > order.index('r_rel'))

    def test_release_without_ownership(self):
        lock = ReadWriteLock()
        with self.assertRaises(SemanticError):
            lock.release_read()
        with self.assertRaises(SemanticError):
            lock.release_write()

if __name__ == '__main__':
    unittest.main()
