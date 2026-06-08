import os
import tempfile
import zipfile
import unittest

from ccai.xmodules.xzipfile import create_archive_of_folder


class TestXZipfile(unittest.TestCase):

    def test_create_archive_creates_destination(self):
        with tempfile.TemporaryDirectory() as td:
            src_dir = os.path.join(td, 'src')
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, 'test.txt'), 'w') as fh:
                fh.write('sample')
            dest_dir = os.path.join(td, 'dest')
            archive_path = os.path.join(dest_dir, 'out.zip')

            create_archive_of_folder(src_dir, archive_path)

            self.assertTrue(os.path.isdir(dest_dir))
            self.assertTrue(os.path.isfile(archive_path))
        return

    def test_create_archive_contents(self):
        with tempfile.TemporaryDirectory() as td:
            src_dir = os.path.join(td, 'src')
            sub_dir = os.path.join(src_dir, 'sub')
            os.makedirs(sub_dir)
            file1 = os.path.join(src_dir, 'file1.txt')
            file2 = os.path.join(sub_dir, 'file2.txt')
            with open(file1, 'w') as fh:
                fh.write('one')
            with open(file2, 'w') as fh:
                fh.write('two')
            archive_path = os.path.join(td, 'archive.zip')

            create_archive_of_folder(src_dir, archive_path)

            with zipfile.ZipFile(archive_path, 'r') as zf:
                names = sorted(zf.namelist())
            self.assertEqual(names, ['file1.txt', 'sub/file2.txt'])
        return


if __name__ == '__main__':
    unittest.main()
