from inventory import add_item, remove_item, total_value
import pytest

def test_add_item():
    inventory = {"apple": 5}
    # Test accumulation
    add_item(inventory, "apple", 3)
    assert inventory["apple"] == 8
    # Test adding new item
    add_item(inventory, "banana", 2)
    assert inventory["banana"] == 2
    # Test negative qty raises ValueError
    try:
        add_item(inventory, "orange", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("add_item should raise ValueError for negative qty")

def test_remove_item():
    inventory = {"apple": 5, "banana": 2}
    # Test removing some quantity
    remove_item(inventory, "apple", 3)
    assert inventory["apple"] == 2
    # Test removing exactly enough to delete key
    remove_item(inventory, "banana", 2)
    assert "banana" not in inventory
    # Test unknown name raises KeyError
    try:
        remove_item(inventory, "orange", 1)
    except KeyError:
        pass
    else:
        raise AssertionError("remove_item should raise KeyError for unknown name")
    # Test removing more than current quantity raises ValueError
    try:
        remove_item(inventory, "apple", 5)
    except ValueError:
        pass
    else:
        raise AssertionError("remove_item should raise ValueError if qty > inventory[name]")

def test_total_value():
    inventory = {"apple": 5, "banana": 2, "orange": 10}
    prices = {"apple": 2.0, "banana": 3.0} # orange is missing
    # apple: 5 * 2.0 = 10.0
    # banana: 2 * 3.0 = 6.0
    # orange: 10 * 0 = 0.0
    # Total = 16.0
    assert total_value(inventory, prices) == 16.0

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
