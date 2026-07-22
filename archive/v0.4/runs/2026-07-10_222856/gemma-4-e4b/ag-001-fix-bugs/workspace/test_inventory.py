import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):

    def setUp(self):
        # Reset inventory for each test
        self.inventory = {}
        self.prices = {"apple": 1.0, "banana": 0.5}

    # --- Test add_item ---
    def test_add_new_item(self):
        result = add_item(self.inventory, "orange", 10)
        self.assertEqual(result["orange"], 10)

    def test_accumulate_existing_item(self):
        # Initial addition
        add_item(self.inventory, "apple", 5)
        # Accumulation
        add_item(self.inventory, "apple", 3)
        self.assertEqual(self.inventory["apple"], 8)

    def test_add_negative_quantity(self):
        with self.assertRaises(ValueError):
            add_item(self.inventory, "grape", -1)

    # --- Test remove_item ---
    def test_remove_partial_stock(self):
        add_item(self.inventory, "apple", 10)
        result = remove_item(self.inventory, "apple", 4)
        self.assertEqual(result["apple"], 6)

    def test_remove_to_zero_delete_key(self):
        add_item(self.inventory, "banana", 5)
        result = remove_item(self.inventory, "banana", 5)
        self.assertNotIn("banana", result)

    def test_remove_unknown_item(self):
        with self.assertRaises(KeyError):
            remove_item(self.inventory, "kiwi", 1)

    def test_remove_too_much_stock(self):
        add_item(self.inventory, "apple", 5)
        with self.assertRaises(ValueError):
            remove_item(self.inventory, "apple", 6)

    # --- Test total_value ---
    def test_calculate_total_value_standard(self):
        add_item(self.inventory, "apple", 10) # Value: 10 * 1.0 = 10.0
        add_item(self.inventory, "banana", 20) # Value: 20 * 0.5 = 10.0
        # Total expected: 20.0
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 20.0)

    def test_calculate_total_value_missing_price(self):
        # Setup inventory with a missing price item (grape: 5 units)
        self.inventory = {"apple": 10, "banana": 20, "grape": 5}
        # Total expected: 10*1.0 + 20*0.5 + 5*0 = 20.0
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 20.0)

    def test_calculate_total_value_missing_price_isolated(self):
        # Setup: Only 'grape' is in inventory, but not in prices
        self.inventory = {"grape": 5}
        total = total_value(self.inventory, self.prices)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_value_empty_inventory(self):
        self.inventory = {}
        total = total_value(self.inventory, self.prices)
        self.assertEqual(total, 0.0)


if __name__ == '__main__':
    unittest.main()