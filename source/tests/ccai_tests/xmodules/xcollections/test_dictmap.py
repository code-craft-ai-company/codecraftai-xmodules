
import unittest

from ccai.xmodules.xcollections.dictmap import DictMap, validate_path_name


class TestDictMap(unittest.TestCase):

    def test_validate_path_name_simple(self):
        parts = validate_path_name('/level1/level2')
        self.assertEqual(parts, ['level1', 'level2'])
        trailing = validate_path_name('/level1/level2/')
        self.assertEqual(trailing, ['level1', 'level2'])

    def test_dictmap_insert_and_lookup(self):
        dmap = DictMap({})
        dmap.insert('/a/b', 1)
        self.assertEqual(dmap.lookup('/a/b'), 1)
        self.assertEqual(dmap.lookup(['a', 'b']), 1)

    def test_dictmap_exists_and_remove(self):
        dmap = DictMap({})
        dmap.insert('/a/b', 1)
        self.assertTrue(dmap.exists('/a/b'))
        removed = dmap.remove('/a/b')
        self.assertEqual(removed, 1)
        self.assertFalse(dmap.exists('/a/b'))
        with self.assertRaises(LookupError):
            dmap.remove('/c/d')

    def test_lookup_default_value(self):
        dmap = DictMap({})
        value = dmap.lookup('/x/y', default=5)
        self.assertEqual(value, 5)
        self.assertEqual(dmap.lookup('/x/y'), 5)

    def test_lookup_default_dict_returns_dictmap(self):
        dmap = DictMap({})
        child = dmap.lookup('/d', default={})
        self.assertIsInstance(child, DictMap)
        child.insert('/name', 'foo')
        self.assertEqual(dmap.lookup('/d/name'), 'foo')

    def test_contains_and_item_access(self):
        dmap = DictMap({})
        dmap['key'] = 123
        self.assertIn('key', dmap)
        self.assertEqual(dmap['key'], 123)

    def test_root_and_is_root_properties(self):
        dmap = DictMap({})
        child = dmap.lookup('/child', default={})
        self.assertTrue(child.is_root)
        self.assertFalse(dmap.is_root)
        self.assertIs(child.root, dmap)


if __name__ == '__main__':
    unittest.main()
