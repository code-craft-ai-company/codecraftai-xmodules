import unittest
from threading import Lock

from automojo.xmodules.xthreading.lockscopes import (
    create_locked_scope,
    create_unlocked_scope,
)


class TestLockScopes(unittest.TestCase):
    def test_locked_scope_acquires_and_releases(self):
        lock = Lock()
        self.assertFalse(lock.locked())
        with create_locked_scope(lock):
            self.assertTrue(lock.locked())
        self.assertFalse(lock.locked())

    def test_unlocked_scope_temporarily_releases(self):
        lock = Lock()
        lock.acquire()
        self.assertTrue(lock.locked())
        with create_unlocked_scope(lock):
            self.assertFalse(lock.locked())
            # Lock can be acquired while in unlocked scope
            lock.acquire()
            lock.release()
        self.assertTrue(lock.locked())
        lock.release()
        self.assertFalse(lock.locked())


if __name__ == '__main__':
    unittest.main()
