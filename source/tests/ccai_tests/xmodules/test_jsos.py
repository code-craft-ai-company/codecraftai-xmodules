import os
import unittest
import tempfile
import json

from ccai.xmodules.jsos import load_jsos_stream_from_file, CHAR_RECORD_SEPERATOR

class TestJSOS(unittest.TestCase):

    def test_load_jsos_stream_from_file(self):
        records = [{"a": 1}, {"b": 2}]
        with tempfile.NamedTemporaryFile('w', delete=False) as tf:
            for rec in records:
                tf.write(json.dumps(rec) + CHAR_RECORD_SEPERATOR)
            fname = tf.name
        try:
            loaded = load_jsos_stream_from_file(fname)
            self.assertEqual(loaded, records)
        finally:
            os.remove(fname)

if __name__ == '__main__':
    unittest.main()
