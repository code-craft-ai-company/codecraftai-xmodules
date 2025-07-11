import unittest

from automojo.xmodules.xcollections.helpers import insert_into_ordered_list_ascending

class TestCollectionHelpers(unittest.TestCase):

    def test_insert_into_empty_list(self):
        ordered = []
        insert_into_ordered_list_ascending(ordered, 1)
        self.assertEqual(ordered, [1])

    def test_insert_at_beginning(self):
        ordered = [2, 3, 4]
        insert_into_ordered_list_ascending(ordered, 1)
        self.assertEqual(ordered, [1, 2, 3, 4])

    def test_insert_in_middle(self):
        ordered = [1, 3, 4]
        insert_into_ordered_list_ascending(ordered, 2)
        self.assertEqual(ordered, [1, 2, 3, 4])

    def test_insert_at_end(self):
        ordered = [1, 2, 3]
        insert_into_ordered_list_ascending(ordered, 4)
        self.assertEqual(ordered, [1, 2, 3, 4])

    def test_insert_duplicate_value(self):
        ordered = [1, 2, 4]
        insert_into_ordered_list_ascending(ordered, 2)
        self.assertEqual(ordered, [1, 2, 2, 4])

if __name__ == '__main__':
    unittest.main()
