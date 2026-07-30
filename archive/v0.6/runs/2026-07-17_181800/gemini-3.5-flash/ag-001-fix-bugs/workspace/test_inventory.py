import unittest
from inventory import add_item, remove_item, total_value

class TestInventory(unittest.TestCase):
    def test_add_item(self):
        inv = {}
        add_item(inv, "apple", 5)
        self.assertEqual(inv, {"apple": 5})
        add_item(inv, "apple", 3)
        self.assertEqual(inv, {"apple": 8})
        with self.assertRaises(ValueError):
            add_item(inv, "apple", -1)

    def test_remove_item(self):
        inv = {"apple": 8, "banana": 2}
        remove_item(inv, "apple", 3)
        self.assertEqual(inv, {"apple": 5, "banana": 2})
        remove_item(inv, "banana", 2)
        self.assertEqual(inv, {"apple": 5})
        with self.assertRaises(KeyError):
            remove_item(inv, "orange", 1)
        with self.assertRaises(ValueError):
            remove_item(inv, "apple", 6)

    def test_total_value(self):
        inv = {"apple": 5, "banana": 2, "orange": 3}
        prices = {"apple": 1.5, "banana": 2.0}
        self.assertEqual(total_value(inv, prices), 5 * 1.5 + 2 * 2.0 + 3 * 0)

if __name__ == "__main__":
    unittest.main()
