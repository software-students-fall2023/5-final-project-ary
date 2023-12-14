import unittest

class TestCollectionFunctions(unittest.TestCase):
    def setUp(self):
        # Setup test data
        self.item1 = CollectionItem(1, "Old Coin", "A rare old coin from 1920.")
        self.item2 = CollectionItem(2, "Vintage Stamp", "A vintage stamp from 1945.")
        self.my_collection = [self.item1, self.item2]

        self.item3 = CollectionItem(3, "Antique Vase", "A beautiful antique vase.")
        self.other_collection = [self.item3]

    def test_add_to_collection(self):
        # Test adding an item
        new_item = CollectionItem(4, "Ancient Manuscript", "A manuscript from the 15th century.")
        add_to_collection(self.my_collection, new_item)
        self.assertIn(new_item, self.my_collection)

    def test_delete_from_collection(self):
        # Test deleting an item
        delete_from_collection(self.my_collection, 1)
        self.assertNotIn(self.item1, self.my_collection)

    def test_view_other_collection(self):
        # Test viewing another collection
        self.assertEqual(view_other_collection(self.other_collection), self.other_collection)

    # Since display_collection() only prints items, we won't write a unit test for it.
    # In a more complex application, you might refactor display_collection to return a string or list for easier testing.

if __name__ == '__main__':
    unittest.main()
