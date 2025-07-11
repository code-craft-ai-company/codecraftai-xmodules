
import os
import unittest
import tempfile

from automojo.xmodules.ximport import import_by_name, import_file

class TestXImport(unittest.TestCase):

    def test_import_by_name(self):
        mod1 = import_by_name('json')
        mod2 = import_by_name('json')
        self.assertIs(mod1, mod2)

    def test_import_file(self):
        with tempfile.TemporaryDirectory() as td:
            modfile = os.path.join(td, 'tempmod.py')
            with open(modfile, 'w') as mf:
                mf.write('VALUE = 42\n')
            mod = import_file('tempmod', modfile, by_file_only=True)
            self.assertEqual(mod.VALUE, 42)

if __name__ == '__main__':
    unittest.main()