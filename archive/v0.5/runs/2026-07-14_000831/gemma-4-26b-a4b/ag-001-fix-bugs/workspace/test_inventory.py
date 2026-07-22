from inventory import add_item, remove_item, total_value
import pytest

def test_add_item():
    inventory = {'apple': 5}
    # Test accumulation
    add_item(inventory, 'apple', 3)
    assert inventory['apple'] == 8
    # Test negative qty
    try:
        add_item(inventory, 'banana', -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for negative qty")
    # Test new item
    add_item(inventory, 'orange', 2)
    assert inventory['orange'] == 2

def test_remove_item():
    inventory = {'apple': 5, 'banana': 2}
    # Test normal removal
    remove_item(inventory, 'apple', 3)
    assert inventory['apple'] == 2
    # Test deletion when reaches 0
    remove_item(inventory, 'banana', 2)
    assert 'banana' not in inventory
    # Test KeyError for unknown name
    try:
        remove_item(inventory, 'orange', 1)
    except KeyError:
        pass
    else:
        raise AssertionError("Should have raised KeyError for unknown name")
    # Test ValueError for removing more than current quantity
    try:
        remove_item(inventory, 'apple', 5)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for removing too much")

def test_total_value():
    inventory = {'apple': 5, 'banana': 2, 'orange': 3}
    prices = {'apple': 1.0, 'banana': 2.0} # orange is missing
    # apple: 5 * 1.0 = 5.0
    # banana: 2 * 2.0 = 4.0
    # orange: 3 * 0 = 0.0
    # Total should be 9.0
    assert total_value(inventory, prices) == 9.0

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
