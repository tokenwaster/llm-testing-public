import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):

    def setUp(self):
        # Setup fresh state for each test
        self.inventory = {}
        self.prices = {"apple": 1.0, "banana": 0.5}

    # --- Tests for add_item ---

    def test_add_new_item(self):
        # Test adding a brand new item
        result = add_item(self.inventory, "orange", 10)
        self.assertEqual(result["orange"], 10)
        self.assertEqual(len(self.inventory), 1)

    def test_accumulate_existing_item(self):
        # Test accumulating quantity
        add_item(self.inventory, "apple", 5)
        result = add_item(self.inventory, "apple", 3)
        self.assertEqual(result["apple"], 8)

    def test_add_negative_quantity_raises_valueerror(self):
        # Test negative quantity handling
        with self.assertRaisesRegex(ValueError, "qty must be non-negative"):
            add_item(self.inventory, "grape", -1)

    # --- Tests for remove_item ---

    def test_remove_existing_item(self):
        # Setup: apple=10
        add_item(self.inventory, "apple", 10)
        result = remove_item(self.inventory, "apple", 3)
        self.assertEqual(result["apple"], 7)

    def test_remove_to_zero_deletes_key(self):
        # Setup: banana=5
        add_item(self.inventory, "banana", 5)
        result = remove_item(self.inventory, "banana", 5)
        self.assertNotIn("banana", result)

    def test_remove_unknown_name_raises_keyerror(self):
        # Test unknown item removal
        with self.assertRaises(KeyError):
            remove_item(self.inventory, "kiwi", 1)

    def test_remove_too_many_raises_valueerror(self):
        # Setup: apple=5
        add_item(self.inventory, "apple", 5)
        # Try to remove 6
        with self.assertRaisesRegex(ValueError, "not enough stock"):
            remove_item(self.inventory, "apple", 6)

    # --- Tests for total_value ---

    def test_calculate_total_value_standard(self):
        # Setup: apple=10 (price 1.0), banana=5 (price 0.5)
        add_item(self.inventory, "apple", 10)
        add_item(self.inventory, "banana", 5)
        # Expected: (10 * 1.0) + (5 * 0.5) = 10 + 2.5 = 12.5
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 12.5)

    def test_missing_price_counts_as_zero(self):
        # Setup: apple=10 (price 1.0), orange=5 (MISSING price)
        add_item(self.inventory, "apple", 10)
        add_item(self.inventory, "orange", 5) # Orange is not in self.prices
        # Expected: (10 * 1.0) + (5 * 0) = 10.0
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 10.0)

    def test_empty_inventory_value(self):
        # Test empty inventory
        total = total_value(self.inventory, self.prices)
        self.assertEqual(total, 0.0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)