from inventory import add_item, remove_item, total_value
import unittest

class TestInventory(unittest.TestCase):
    def test_add_item_accumulation(self):
        inventory = {'apple': 5}
        add_item(inventory, 'apple', 3)
        self.assertEqual(inventory['apple'], 8)
        
        add_item(inventory, 'banana', 2)
        self.assertEqual(inventory['banana'], 2)

    def test_add_item_negative_qty(self):
        with self.assertRaises(ValueError):
            add_item({}, 'apple', -1)

    def test_remove_item_success(self):
        inventory = {'apple': 5, 'banana': 2}
        remove_item(inventory, 'apple', 3)
        self.assertEqual(inventory['apple'], 2)
        remove_item(inventory, 'banana', 2)
        self.assertNotIn('banana', inventory)

    def test_remove_item_unknown_name(self):
        with self.assertRaises(KeyError):
            remove_item({'apple': 5}, 'banana', 1)

    def test_remove_item_too_much(self):
        with self.assertRaises(ValueError):
            remove_item({'apple': 5}, 'apple', 6)

    def test_total_value_all_present(self):
        inventory = {'apple': 5, 'banana': 2}
        prices = {'apple': 1.0, 'banana': 2.0}
        self.assertEqual(total_value(inventory, prices), 9.0)

    def test_total_value_missing_prices(self):
        inventory = {'apple': 5, 'banana': 2, 'cherry': 10}
        prices = {'apple': 1.0, 'banana': 2.0}
        # cherry is missing from prices, should count as 0
        self.assertEqual(total_value(inventory, prices), 9.0)

if __name__ == "__main__":
    unittest.main()
