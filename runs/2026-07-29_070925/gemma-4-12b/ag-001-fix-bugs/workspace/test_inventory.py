from inventory import add_item, remove_item, total_value

def test():
    # Test add_item accumulation
    inv = {}
    add_item(inv, "apple", 10)
    add_item(inv, "apple", 5)
    assert inv["apple"] == 15, f"Expected 15, got {inv['apple']}"
    
    # Test add_item ValueError
    try:
        add_item(inv, "banana", -1)
        assert False, "Should have raised ValueError for negative qty"
    except ValueError:
        pass

    # Test remove_item logic
    inv = {"orange": 10}
    remove_item(inv, "orange", 4)
    assert inv["orange"] == 6
    remove_item(inv, "orange", 6)
    assert "orange" not in inv
    
    # Test remove_item KeyError (name doesn't exist)
    try:
        remove_item(inv, "grape", 1)
        assert False, "Should have raised KeyError for missing item"
    except KeyError:
        pass

    # Test remove_item ValueError (not enough stock)
    inv = {"pear": 5}
    try:
        remove_item(inv, "pear", 10)
        assert False, "Should have raised ValueError for over-removal"
    except ValueError:
        pass

    # Test total_value logic and missing prices
    inv = {"apple": 10, "banana": 5}
    prices = {"apple": 2.0, "orange": 3.0} # banana is missing
    # apple: 10 * 2.0 = 20.0
    # banana: 5 * 0 (missing) = 0.0
    val = total_value(inv, prices)
    assert val == 20.0, f"Expected 20.0, got {val}"

    print("All tests passed!")

if __name__ == "__main__":
    test()
