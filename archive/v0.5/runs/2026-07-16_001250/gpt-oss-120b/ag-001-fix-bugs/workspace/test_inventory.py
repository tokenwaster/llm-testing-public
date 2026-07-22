import unittest, inventory

class TestInventory(unittest.TestCase):
    def test_add(self):
        inv = {}
        inventory.add_item(inv, 'apple', 5)
        self.assertEqual(inv, {'apple':5})
        inventory.add_item(inv, 'apple', 3)
        self.assertEqual(inv, {'apple':8})
        with self.assertRaises(ValueError):
            inventory.add_item(inv, 'banana', -1)
    def test_remove(self):
        inv = {'apple':5}
        inventory.remove_item(inv, 'apple', 2)
        self.assertEqual(inv, {'apple':3})
        inventory.remove_item(inv, 'apple', 3)
        self.assertEqual(inv, {})
        with self.assertRaises(KeyError):
            inventory.remove_item(inv, 'banana', 1)
        inv = {'apple':2}
        with self.assertRaises(ValueError):
            inventory.remove_item(inv, 'apple', 3)
    def test_total(self):
        inv = {'apple':2, 'banana':3}
        prices = {'apple':1.5, 'banana':2.0}
        self.assertAlmostEqual(inventory.total_value(inv, prices), 2*1.5+3*2.0)
        # missing price
        prices = {'apple':1.5}
        self.assertAlmostEqual(inventory.total_value(inv, prices), 2*1.5+3*0)

if __name__ == '__main__':
    unittest.main()
