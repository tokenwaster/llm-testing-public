import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):

    def setUp(self):
        # Reset inventory for each test
        self.inventory = {}
        self.prices = {"apple": 1.0, "banana": 0.5}

    # --- Tests for add_item ---
    def test_add_new_item(self):
        inv = self.inventory.copy()
        result = add_item(inv, "orange", 10)
        self.assertEqual(result["orange"], 10)

    def test_accumulate_existing_item(self):
        # Setup initial state
        self.inventory["apple"] = 5
        inv = self.inventory.copy()
        # Add more apples
        add_item(inv, "apple", 3)
        self.assertEqual(inv["apple"], 8)

    def test_add_negative_quantity_raises_valueerror(self):
        inv = self.inventory.copy()
        with self.assertRaises(ValueError):
            add_item(inv, "grape", -1)

    # --- Tests for remove_item ---
    def test_remove_existing_item(self):
        self.inventory["apple"] = 5
        inv = self.inventory.copy()
        result = remove_item(inv, "apple", 2)
        self.assertEqual(result["apple"], 3)

    def test_remove_to_zero_deletes_key(self):
        self.inventory["banana"] = 5
        inv = self.inventory.copy()
        remove_item(inv, "banana", 5)
        self.assertNotIn("banana", inv)

    def test_unknown_name_raises_keyerror(self):
        inv = self.inventory.copy()
        with self.assertRaises(KeyError):
            remove_item(inv, "kiwi", 1)

    def test_removing_too_much_raises_valueerror(self):
        self.inventory["apple"] = 2
        inv = self.inventory.copy()
        with self.assertRaises(ValueError):
            remove_item(inv, "apple", 3)

    # --- Tests for total_value ---
    def test_basic_total_value(self):
        self.inventory["apple"] = 10
        self.inventory["banana"] = 20
        expected = (10 * 1.0) + (20 * 0.5) # 10 + 10 = 20.0
        self.assertAlmostEqual(total_value(self.inventory, self.prices), expected)

    def test_missing_price_counts_as_zero(self):
        # 'orange' is in inventory but not in prices dict
        self.inventory["apple"] = 10
        self.inventory["orange"] = 5 # Price missing
        expected = (10 * 1.0) + (5 * 0.0) # 10 + 0 = 10.0
        self.assertAlmostEqual(total_value(self.inventory, self.prices), expected)

    def test_empty_inventory_value(self):
        self.inventory = {}
        expected = 0.0
        self.assertAlmostEqual(total_value(self.inventory, self.prices), expected)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)