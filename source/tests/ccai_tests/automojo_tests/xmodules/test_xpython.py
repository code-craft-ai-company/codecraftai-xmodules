import os
import sys
import unittest
import tempfile

from ccai.xmodules.xpython import in_python_path, prepend_python_path, append_python_path

class TestXPython(unittest.TestCase):

    def test_in_python_path(self):
        with tempfile.TemporaryDirectory() as td:
            # Directory should not be in sys.path initially
            self.assertFalse(in_python_path(td))

            # Add the directory and verify detection
            sys.path.insert(0, td)
            try:
                self.assertTrue(in_python_path(td))
            finally:
                sys.path.remove(td)
        return
    
    def test_prepend_python_path(self):
        with tempfile.TemporaryDirectory() as td:
            orig_sys_path = list(sys.path)
            orig_env = os.environ.get("PYTHONPATH")

            if td in sys.path:
                sys.path.remove(td)

            try:
                prepend_python_path(td)
                self.assertEqual(sys.path[0], td)

                env_val = os.environ.get("PYTHONPATH")
                if orig_env is None:
                    self.assertEqual(env_val, td)
                else:
                    self.assertEqual(env_val.split(os.pathsep)[0], td)
            finally:
                sys.path[:] = orig_sys_path
                if orig_env is None:
                    os.environ.pop("PYTHONPATH", None)
                else:
                    os.environ["PYTHONPATH"] = orig_env
        return
    
    def test_append_python_path(self):
        with tempfile.TemporaryDirectory() as td:
            orig_sys_path = list(sys.path)
            orig_env = os.environ.get("PYTHONPATH")

            if td in sys.path:
                sys.path.remove(td)

            try:
                append_python_path(td)
                self.assertEqual(sys.path[-1], td)

                env_val = os.environ.get("PYTHONPATH")
                if orig_env is None:
                    self.assertEqual(env_val, td)
                else:
                    self.assertEqual(env_val.split(os.pathsep)[-1], td)
            finally:
                sys.path[:] = orig_sys_path
                if orig_env is None:
                    os.environ.pop("PYTHONPATH", None)
                else:
                    os.environ["PYTHONPATH"] = orig_env
        return

if __name__ == '__main__':
    unittest.main()
