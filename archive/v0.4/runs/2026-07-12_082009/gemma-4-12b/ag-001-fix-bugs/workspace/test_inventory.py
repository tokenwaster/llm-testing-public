import inventory

def test_inventory():
    # Test add_item accumulation
    inv = {"apple": 5}
    inventory.add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
    inventory.add_item(inv, "banana", 2)
    assert inv["banana"] == 2, f"Expected 2, got {inv['banana']}"
    
    # Test add_item negative qty
    try:
        inventory.add_item(inv, "orange", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Test remove_item basic
    inv = {"apple": 10}
    inventory.remove_item(inv, "apple", 4)
    assert inv["apple"] == 6, f"Expected 6, got {inv['apple']}"

    # Test remove_item delete key at 0
    inventory.remove_item(inv, "apple", 6)
    assert "apple" not in inv, "Key should be deleted when quantity is 0"

    # Test remove_item KeyError
    try:
        inventory.remove_item(inv, "pear", 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass

    # Test remove_item ValueError (too many)
    try:
        inv2 = {"apple": 5}
        inventory.remove_item(inv2, "apple", 6)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Test total_value with missing prices
    inv3 = {"apple": 10, "banana": 5}
    prices = {"apple": 1.0} # banana is missing
    val = inventory.total_value(inv3, prices)
    assert val == 10.0, f"Expected 10.0, got {val}"

    print("All tests passed!")

if __name__ == "__main__":
    test_inventory()
