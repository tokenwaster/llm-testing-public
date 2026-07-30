from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {}
    # Test accumulation
    add_item(inv, "apple", 10)
    assert inv["apple"] == 10
    add_item(inv, "apple", 5)
    assert inv["apple"] == 15
    # Test negative qty
    try:
        add_item(inv, "banana", -1)
    except ValueError:
        pass
    else:
        print("Fail: add_item did not raise ValueError for negative qty")
    print("add_item tests passed")

def test_remove_item():
    inv = {"apple": 10}
    # Test normal removal
    remove_item(inv, "apple", 5)
    assert inv["apple"] == 5
    # Test remove to zero (deletion)
    remove_item(inv, "apple", 5)
    assert "apple" not in inv
    # Test KeyError
    try:
        remove_item(inv, "orange", 1)
    except KeyError:
        pass
    else:
        print("Fail: remove_item did not raise KeyError for missing item")
    # Test ValueError (too much)
    inv = {"apple": 5}
    try:
        remove_item(inv, "apple", 10)
    except ValueError:
        pass
    else:
        print("Fail: remove_item did not raise ValueError for removing too much")
    print("remove_item tests passed")

def test_total_value():
    inv = {"apple": 10, "banana": 5}
    prices = {"apple": 1.0} # banana missing
    # Should be 10 * 1.0 + 5 * 0 = 10.0
    val = total_value(inv, prices)
    assert val == 10.0
    print("total_value tests passed")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
