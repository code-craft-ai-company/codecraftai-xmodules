import os
import unittest
import tempfile

from automojo.xmodules.fspath import (
    expand_path,
    get_expanded_path,
    normalize_name_for_path,
    ensure_directory_is_package
)

class TestFspath(unittest.TestCase):

    def test_expand_path_defaults(self):
        os.environ['TEST_EXPAND'] = 'subdir'
        try:
            path_in = os.path.join('~', '${TEST_EXPAND}')
            expected = os.path.abspath(os.path.join(os.path.expanduser('~'), 'subdir'))
            result = expand_path(path_in)
            self.assertEqual(result, expected)
        finally:
            del os.environ['TEST_EXPAND']
        return
    
    def test_expand_and_get_expanded_path(self):
        with tempfile.TemporaryDirectory() as td:
            os.environ['TDIR'] = td
            p1 = expand_path('~/')
            self.assertTrue(os.path.isdir(p1))
            p2 = expand_path('$TDIR/file')
            self.assertEqual(p2, os.path.join(td, 'file'))
            p3 = get_expanded_path('~/dummy')
            self.assertEqual(p3, os.path.abspath(os.path.expanduser('~/dummy')))
        return

    def test_normalize_name_for_path(self):
        self.assertEqual(normalize_name_for_path('Test:Value,Name'), 'TestValueName')
        return

    def test_expand_path_custom_order(self):
        def add_suffix(p):
            return p + 'A'

        def to_upper(p: str):
            return p.upper()

        result = expand_path('path', expansions=[add_suffix, to_upper])
        self.assertEqual(result, 'PATHA')
        return

    def test_ensure_directory_is_package(self):
        with tempfile.TemporaryDirectory() as td:
            ensure_directory_is_package(td, "Sample Package")
            init_file = os.path.join(td, '__init__.py')
            self.assertTrue(os.path.isfile(init_file))

            with open(init_file, 'r') as initf:
                content = initf.read().splitlines()

            self.assertEqual(content[0], '"""')
            self.assertIn('Sample Package', content[1])
            self.assertEqual(content[2], '"""')
        return


if __name__ == '__main__':
    unittest.main()
