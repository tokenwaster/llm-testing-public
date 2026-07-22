import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):
    def setUp(self):
        # Reset inventory for each test
        self.inventory = {}
        self.prices = {"apple": 1.0, "banana": 0.5, "cherry": 2.0}

    # --- Tests for add_item ---
    def test_add_new_item(self):
        inv = {}
        result = add_item(inv, "grape", 10)
        self.assertEqual(result, {"grape": 10})

    def test_accumulate_existing_item(self):
        inv = {"apple": 5}
        result = add_item(inv, "apple", 3)
        self.assertEqual(result, {"apple": 8})

    def test_add_negative_quantity(self):
        inv = {}
        with self.assertRaises(ValueError):
            add_item(inv, "test", -1)

    # --- Tests for remove_item ---
    def test_remove_existing_item(self):
        inv = {"apple": 5}
        result = remove_item(inv, "apple", 2)
        self.assertEqual(result, {"apple": 3})

    def test_remove_to_zero(self):
        inv = {"banana": 3}
        result = remove_item(inv, "banana", 3)
        self.assertNotIn("banana", result)
        self.assertEqual(result, {})

    def test_remove_unknown_item(self):
        inv = {"apple": 5}
        with self.assertRaises(KeyError):
            remove_item(inv, "kiwi", 1)

    def test_remove_too_many(self):
        inv = {"apple": 2}
        with self.assertRaises(ValueError):
            remove_item(inv, "apple", 3)

    # --- Tests for total_value ---
    def test_total_value_standard(self):
        inv = {"apple": 10, "banana": 4}
        # (10 * 1.0) + (4 * 0.5) = 10 + 2 = 12.0
        self.assertAlmostEqual(total_value(inv, self.prices), 12.0)

    def test_total_value_missing_price(self):
        # 'grape' is in inventory but not in prices (should count as 0 price)
        inv = {"apple": 5, "grape": 10}
        prices = {"apple": 2.0} # Only apple has a defined price
        # (5 * 2.0) + (10 * 0) = 10.0
        self.assertAlmostEqual(total_value(inv, prices), 10.0)

    def test_total_value_empty_inventory(self):
        inv = {}
        self.assertEqual(total_value(inv, self.prices), 0.0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)