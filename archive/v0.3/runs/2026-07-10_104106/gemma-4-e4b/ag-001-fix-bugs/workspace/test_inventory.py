import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):

    def setUp(self):
        # Setup a fresh inventory for each test
        self.inventory = {}
        self.prices = {"apple": 1.0, "banana": 0.5, "cherry": 2.0}

    # --- Test add_item ---

    def test_add_new_item(self):
        # Add a brand new item
        result = add_item(self.inventory, "apple", 10)
        self.assertEqual(self.inventory["apple"], 10)
        self.assertIs(result, self.inventory)

    def test_accumulate_existing_item(self):
        # Add an item and then accumulate it
        add_item(self.inventory, "banana", 5)
        result = add_item(self.inventory, "banana", 3)
        self.assertEqual(self.inventory["banana"], 8)
        self.assertIs(result, self.inventory)

    def test_add_negative_quantity_raises_valueerror(self):
        # Test negative quantity handling
        with self.assertRaisesRegex(ValueError, "qty must be non-negative"):
            add_item(self.inventory, "apple", -1)

    # --- Test remove_item ---

    def test_remove_existing_item(self):
        # Setup: 10 apples
        self.inventory["apple"] = 10
        # Action: Remove 3 apples
        result = remove_item(self.inventory, "apple", 3)
        self.assertEqual(self.inventory["apple"], 7)
        self.assertIs(result, self.inventory)

    def test_remove_to_zero_deletes_key(self):
        # Setup: 5 bananas
        self.inventory["banana"] = 5
        # Action: Remove all 5
        result = remove_item(self.inventory, "banana", 5)
        self.assertNotIn("banana", self.inventory)
        self.assertIs(result, self.inventory)

    def test_remove_unknown_name_raises_keyerror(self):
        # Test unknown item removal
        with self.assertRaises(KeyError):
            remove_item(self.inventory, "grape", 1)

    def test_remove_too_much_stock_raises_valueerror(self):
        # Setup: 5 apples
        self.inventory["apple"] = 5
        # Action: Try to remove 6
        with self.assertRaisesRegex(ValueError, "not enough stock"):
            remove_item(self.inventory, "apple", 6)

    def test_remove_from_empty_inventory(self):
        # Ensure nothing happens if the item was already removed (and thus not in inventory)
        self.inventory = {} # Reset just to be safe
        with self.assertRaises(KeyError):
            remove_item(self.inventory, "apple", 1)

    # --- Test total_value ---

    def test_calculate_total_value_standard(self):
        # Setup: apple=10 (10*1.0), banana=5 (5*0.5)
        self.inventory["apple"] = 10
        self.inventory["banana"] = 5
        # Expected: 10 + 2.5 = 12.5
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 12.5)

    def test_missing_price_counts_as_zero(self):
        # Setup: apple=10 (10*1.0), cherry=5 (5*2.0). Add 'grape' which is missing from prices.
        self.inventory["apple"] = 10
        self.inventory["cherry"] = 5
        self.inventory["grape"] = 2 # Price for grape is missing
        # Expected: 10 + 10 + (2 * 0) = 20.0
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 20.0)

    def test_empty_inventory_value(self):
        # Test empty inventory
        self.inventory = {}
        total = total_value(self.inventory, self.prices)
        self.assertEqual(total, 0.0)

if __name__ == '__main__':
    unittest.main()