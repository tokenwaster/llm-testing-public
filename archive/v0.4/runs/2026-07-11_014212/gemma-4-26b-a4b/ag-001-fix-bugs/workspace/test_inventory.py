from inventory import add_item, remove_item, total_value
import unittest

class TestInventory(unittest.TestCase):
    def test_add_item_accumulation(self):
        inventory = {'apple': 5}
        add_item(inventory, 'apple', 3)
        self.assertEqual(inventory['apple'], 8)

    def test_add_item_negative_qty(self):
        inventory = {}
        with self.assertRaises(ValueError):
            add_item(inventory, 'apple', -1)

    def test_remove_item_success(self):
        inventory = {'apple': 5}
        remove_item(inventory, 'apple', 3)
        self.assertEqual(inventory['apple'], 2)

    def test_remove_item_deletion(self):
        inventory = {'apple': 5}
        remove_item(inventory, 'apple', 5)
        self.assertNotIn('apple', inventory)

    def test_remove_item_unknown_name(self):
        inventory = {'apple': 5}
        with self.assertRaises(KeyError):
            remove_item(inventory, 'banana', 1)

    def test_remove_item_too_many(self):
        inventory = {'apple': 5}
        with self.assertRaises(ValueError):
            remove_item(inventory, 'apple', 6)

    def test_total_value_calculation(self):
        inventory = {'apple': 5, 'banana': 10}
        prices = {'apple': 2.0, 'banana': 1.0}
        # (5 * 2.0) + (10 * 1.0) = 10 + 10 = 20
        self.assertEqual(total_value(inventory, prices), 20.0)

    def test_total_value_missing_price(self):
        inventory = {'apple': 5, 'banana': 10}
        prices = {'apple': 2.0}
        # (5 * 2.0) + (10 * 0) = 10
        self.assertEqual(total_value(inventory, prices), 10.0)

if __name__ == '__main__':
    unittest.main()
