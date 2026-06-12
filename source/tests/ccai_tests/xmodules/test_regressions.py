"""
    Regression tests for previously-uncovered defects in ccai.xmodules:
    the ReadWriteLock default-timeout crash, the missing Context module,
    EnhancedLogger.exception() recursion, EventedVariable value-state, and the
    collect_python_modules max_depth pruning bug.
"""

import logging
import os
import tempfile
import unittest

from ccai.xmodules.xthreading.readwritelock import ReadWriteLock
from ccai.xmodules.xcollections.wellknown import ContextSingleton
from ccai.xmodules.xcollections.context import Context
from ccai.xmodules.xlogging.enhancedloggers import EnhancedLogger
from ccai.xmodules.eventing.enumerations import EventedVariableState
from ccai.xmodules.eventing.eventedvariable import EventedVariable
from ccai.xmodules.fspath import collect_python_modules


class TestReadWriteLockDefaultTimeout(unittest.TestCase):
    """
        ReadWriteLock.acquire_read/acquire_write must work with the default
        timeout=None (previously raised TypeError: float + NoneType).
    """

    def test_acquire_read_no_timeout(self) -> None:
        rwl = ReadWriteLock()
        rwl.acquire_read()
        rwl.release_read()
        return

    def test_acquire_write_no_timeout(self) -> None:
        rwl = ReadWriteLock()
        rwl.acquire_write()
        rwl.release_write()
        return


class TestContext(unittest.TestCase):
    """
        The Context class and ContextSingleton must import and function
        (previously ModuleNotFoundError on a missing context module).
    """

    def test_context_insert_lookup(self) -> None:
        ctx = Context()
        ctx.insert("/db/host", "h1")
        self.assertEqual(ctx.lookup("/db/host"), "h1")
        self.assertTrue(ctx.exists("/db/host"))
        return

    def test_context_singleton_is_shared(self) -> None:
        a = ContextSingleton()
        b = ContextSingleton()
        self.assertIs(a, b)
        return


class TestEnhancedLoggerException(unittest.TestCase):
    """
        EnhancedLogger.exception() must delegate (previously infinitely recursed).
    """

    def test_exception_does_not_recurse(self) -> None:
        el = EnhancedLogger(logging.getLogger("ccai.test.regression"))
        try:
            raise ValueError("boom")
        except ValueError:
            # Would RecursionError before the fix.
            el.exception("handled")
        return


class TestEventedVariableState(unittest.TestCase):
    """
        An EventedVariable constructed with a value (no explicit timestamp) must
        report Valid with non-None created/updated (previously UnInitialized/None).
    """

    def test_value_without_timestamp_is_valid(self) -> None:
        ev = EventedVariable("k", "n", None, value=123)
        self.assertEqual(ev.state, EventedVariableState.Valid)
        self.assertIsNotNone(ev.created)
        self.assertIsNotNone(ev.updated)
        return


class TestCollectPythonModulesDepth(unittest.TestCase):
    """
        collect_python_modules(max_depth=1) must keep valid same-depth files in
        sibling subtrees (previously break aborted the whole walk).
    """

    def test_max_depth_prunes_without_dropping_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "sub1", "deep"))
            os.makedirs(os.path.join(td, "sub2"))
            for rel in ["a.py", "sub1/b.py", "sub1/deep/x.py", "sub2/c.py"]:
                full = os.path.join(td, rel)
                with open(full, "w") as f:
                    f.write("# module\n")

            found = collect_python_modules(td, max_depth=1)
            leaves = sorted(os.path.basename(p) for p in found)

            self.assertIn("a.py", leaves)
            self.assertIn("b.py", leaves)
            self.assertIn("c.py", leaves)   # sibling subtree not dropped
            self.assertNotIn("x.py", leaves)  # depth 2 excluded
        return


if __name__ == "__main__":
    unittest.main()
