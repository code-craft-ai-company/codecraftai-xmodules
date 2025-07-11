import unittest

from automojo.xmodules.xcollections.mergemap import (
    MergeMap,
    validate_path_name
)


class TestMergeMap(unittest.TestCase):

    def test_validate_path_name(self):
        self.assertEqual(validate_path_name('/a/b/'), ['a', 'b'])
        self.assertEqual(validate_path_name('a/b'), ['b'])

    def test_fromkeys_creates_defaults(self):
        mm = MergeMap.fromkeys(['x', 'y'], 0)
        self.assertIn('x', mm)
        self.assertIn('y', mm)
        self.assertEqual(mm['x'], 0)
        self.assertEqual(mm['y'], 0)

    def test_basic_set_and_get(self):
        mm = MergeMap({})
        mm['a'] = 1
        mm['b'] = 2
        self.assertEqual(mm['a'], 1)
        self.assertEqual(mm.get('b'), 2)
        self.assertEqual(mm.get('c', 5), 5)
        self.assertIn('a', mm)
        self.assertEqual(len(mm), 2)

    def test_new_child_behavior(self):
        base = MergeMap({'a': 1})
        child = base.new_child({'b': 2})
        self.assertEqual(child['b'], 2)
        self.assertEqual(child['a'], 1)
        # Changes to the child should not modify the base
        child['a'] = 3
        self.assertEqual(base['a'], 1)

    def test_merging_list_values(self):
        mm = MergeMap({'a': [1, 2]}, {'a': [2, 3]})
        self.assertEqual(mm['a'], [1, 2, 3])

    def test_merging_dict_values(self):
        mm = MergeMap({'a': {'x': 1}}, {'a': {'y': 2}})
        val = mm['a']
        self.assertIsInstance(val, MergeMap)
        self.assertEqual(val['x'], 1)
        self.assertEqual(val['y'], 2)

    def test_flatten_nested_mergemap(self):
        mm = MergeMap({'a': {'x': 1}}, {'a': {'y': 2}})
        flat = mm.flatten()
        self.assertEqual(flat, {'a': {'x': 1, 'y': 2}})

    def test_delete_raises_key_error(self):
        mm = MergeMap({'a': 1})
        with self.assertRaises(KeyError):
            del mm['a']


if __name__ == '__main__':
    unittest.main()
