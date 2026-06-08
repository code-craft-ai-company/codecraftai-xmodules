
import unittest

from ccai.xmodules.xformatting import (
    indent_line,
    indent_lines,
    indent_lines_list,
    split_and_indent_lines,
    format_command_result
)

class TestXFormatting(unittest.TestCase):

    def test_indent_line(self):
        self.assertEqual(indent_line('abc', 2, 2), '    abc')
        return
    
    def test_indent_lines(self):
        self.assertEqual(indent_lines('a\nb', 1, 2), '  a\n  b')
        return
    
    def test_indent_lines_list(self):
        self.assertEqual(indent_lines_list(['a', 'b'], 1, 2), ['  a', '  b'])
        return
    
    def test_split_and_indent_lines(self):
        self.assertEqual(split_and_indent_lines('  a\n  b', 1, 2), ['  a', '  b'])
        return

    def test_format_command_result(self):
        msg = format_command_result('MSG', 'cmd', 0, 'out', 'err', [0], 'TARGET')
        self.assertIn('MSG', msg)
        self.assertIn('COMMAND cmd', msg)
        self.assertIn('STATUS: 0', msg)
        self.assertIn('EXPECTED: [0]', msg)
        self.assertIn('TARGET: TARGET', msg)
        self.assertIn('STDOUT:', msg)
        self.assertIn('STDERR:', msg)
        return

if __name__ == '__main__':
    unittest.main()
