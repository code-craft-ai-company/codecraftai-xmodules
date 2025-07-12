import os
import unittest

from automojo.xmodules.xinspect import (
    get_current_function_name,
    get_caller_function_name,
    get_module_ancestry,
    is_typed_from_type,
)


class TestXInspect(unittest.TestCase):

    def test_get_current_function_name(self):
        def sample():
            return get_current_function_name()
        self.assertEqual(sample(), "sample")
        return

    def test_get_caller_function_name(self):
        def parent():
            def child():
                return get_caller_function_name()
            return child()
        self.assertEqual(parent(), "parent")
        return

    def test_get_module_ancestry(self):
        import os.path as osp
        mods = get_module_ancestry("os.path")
        self.assertEqual(len(mods), 2)
        self.assertIs(mods[0], os)
        self.assertIs(mods[1], osp)
        return

    def test_is_typed_from_type(self):
        class Sample:
            pass
        self.assertTrue(is_typed_from_type(Sample))
        self.assertTrue(is_typed_from_type(int))
        self.assertFalse(is_typed_from_type(Sample()))
        return


if __name__ == "__main__":
    unittest.main()
