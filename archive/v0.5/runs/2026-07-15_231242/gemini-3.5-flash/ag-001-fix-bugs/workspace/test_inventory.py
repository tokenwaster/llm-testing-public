import inventory

def test_inventory():
    # Test add_item
    inv = {}
    inventory.add_item(inv, "apple", 5)
    assert inv == {"apple": 5}
    inventory.add_item(inv, "apple", 3)
    assert inv == {"apple": 8}
    try:
        inventory.add_item(inv, "banana", -1)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    # Test remove_item
    inventory.remove_item(inv, "apple", 3)
    assert inv == {"apple": 5}
    try:
        inventory.remove_item(inv, "banana", 1)
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    try:
        inventory.remove_item(inv, "apple", 6)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    inventory.remove_item(inv, "apple", 5)
    assert inv == {}

    # Test total_value
    inv = {"apple": 5, "banana": 3, "cherry": 10}
    prices = {"apple": 1.5, "banana": 2.0}
    val = inventory.total_value(inv, prices)
    assert val == 5 * 1.5 + 3 * 2.0 + 10 * 0, f"Expected 13.5, got {val}"
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_inventory()
