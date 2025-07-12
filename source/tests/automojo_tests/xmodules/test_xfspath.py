import os
import unittest

from automojo.xmodules.xfspath import expand_path


class TestXFspath(unittest.TestCase):

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

    def test_expand_path_custom_order(self):
        def add_suffix(p):
            return p + 'A'

        def to_upper(p):
            return p.upper()

        result = expand_path('path', expansions=[add_suffix, to_upper])
        self.assertEqual(result, 'PATHA')
        return


if __name__ == '__main__':
    unittest.main()
