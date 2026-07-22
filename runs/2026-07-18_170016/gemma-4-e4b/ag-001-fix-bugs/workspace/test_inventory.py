import unittest
from inventory_fixed import add_item, remove_item, total_value

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

    def test_add_accumulating_existing_item(self):
        # Test accumulating quantity
        add_item(self.inventory, "apple", 5)
        result = add_item(self.inventory, "apple", 3)
        self.assertEqual(result["apple"], 8)

    def test_add_negative_quantity_raises_valueerror(self):
        # Test negative quantity constraint
        with self.assertRaisesRegex(ValueError, "qty must be non-negative"):
            add_item(self.inventory, "grape", -1)

    # --- Tests for remove_item ---

    def test_remove_existing_item(self):
        # Setup: Add item first
        add_item(self.inventory, "apple", 10)
        # Action: Remove some quantity
        result = remove_item(self.inventory, "apple", 4)
        self.assertEqual(result["apple"], 6)

    def test_remove_to_zero_deletes_key(self):
        # Setup: Add item with small quantity
        add_item(self.inventory, "banana", 5)
        # Action: Remove exactly the current amount
        result = remove_item(self.inventory, "banana", 5)
        self.assertNotIn("banana", result)
        self.assertEqual(len(result), 0)

    def test_remove_unknown_name_raises_keyerror(self):
        # Test unknown item name
        with self.assertRaisesRegex(KeyError, "grape"):
            remove_item(self.inventory, "grape", 1)

    def test_remove_too_much_stock_raises_valueerror(self):
        # Setup: Add item with small quantity
        add_item(self.inventory, "apple", 5)
        # Action: Attempt to remove more than available
        with self.assertRaisesRegex(ValueError, "not enough stock"):
            remove_item(self.inventory, "apple", 6)

    # --- Tests for total_value ---

    def test_total_value_standard(self):
        # Setup: Inventory and Prices
        add_item(self.inventory, "apple", 10) # Value: 10 * 1.0 = 10.0
        add_item(self.inventory, "banana", 5) # Value: 5 * 0.5 = 2.5
        # Total expected: 12.5
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 12.5)

    def test_total_value_missing_price_counts_as_zero(self):
        # Setup: Inventory includes 'grape' which is not in prices
        add_item(self.inventory, "apple", 10) # Value: 10 * 1.0 = 10.0
        add_item(self.inventory, "grape", 20) # Price missing -> counts as 0. Value: 20 * 0 = 0.0
        # Total expected: 10.0
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 10.0)

    def test_total_value_empty_inventory(self):
        # Test empty inventory
        total = total_value(self.inventory, self.prices)
        self.assertEqual(total, 0.0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)