import unittest
import inventory


class TestInventory(unittest.TestCase):

    def test_add_item_accumulates(self):
        inv = {}
        inventory.add_item(inv, "apple", 5)
        self.assertEqual(inv, {"apple": 5})
        inventory.add_item(inv, "apple", 3)
        self.assertEqual(inv, {"apple": 8})

    def test_add_item_negative_qty(self):
        inv = {"apple": 5}
        with self.assertRaises(ValueError):
            inventory.add_item(inv, "apple", -1)

    def test_remove_item_success(self):
        inv = {"apple": 5, "banana": 2}
        inventory.remove_item(inv, "apple", 3)
        self.assertEqual(inv, {"apple": 2, "banana": 2})

    def test_remove_item_exact_zero_deletes_key(self):
        inv = {"apple": 5, "banana": 2}
        inventory.remove_item(inv, "banana", 2)
        self.assertEqual(inv, {"apple": 5})
        self.assertNotIn("banana", inv)

    def test_remove_item_unknown_name(self):
        inv = {"apple": 5}
        with self.assertRaises(KeyError):
            inventory.remove_item(inv, "orange", 1)

    def test_remove_item_too_much_qty(self):
        inv = {"apple": 5}
        with self.assertRaises(ValueError):
            inventory.remove_item(inv, "apple", 6)

    def test_remove_item_negative_qty(self):
        inv = {"apple": 5}
        with self.assertRaises(ValueError):
            inventory.remove_item(inv, "apple", -1)

    def test_total_value_normal(self):
        inv = {"apple": 5, "banana": 2}
        prices = {"apple": 1.5, "banana": 0.5}
        val = inventory.total_value(inv, prices)
        self.assertEqual(val, 8.5)
        self.assertIsInstance(val, float)

    def test_total_value_missing_prices(self):
        inv = {"apple": 5, "banana": 2, "orange": 10}
        prices = {"apple": 2.0}
        val = inventory.total_value(inv, prices)
        self.assertEqual(val, 10.0)
        self.assertIsInstance(val, float)

    def test_total_value_empty_inventory(self):
        val = inventory.total_value({}, {"apple": 1.0})
        self.assertEqual(val, 0.0)
        self.assertIsInstance(val, float)


if __name__ == "__main__":
    unittest.main()
