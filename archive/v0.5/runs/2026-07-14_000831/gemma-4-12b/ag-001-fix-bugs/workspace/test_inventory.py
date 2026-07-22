from inventory import add_item, remove_item, total_value

def test_add_item():
    inventory = {}
    # Test accumulation
    add_item(inventory, "apple", 10)
    assert inventory["apple"] == 10
    add_item(inventory, "apple", 5)
    assert inventory["apple"] == 15
    print("test_add_item (accumulation) passed")

    # Test negative qty
    try:
        add_item(inventory, "banana", -1)
    except ValueError:
        print("test_add_item (negative qty) passed")
    else:
        print("test_add_item (negative qty) FAILED")

def test_remove_item():
    inventory = {"apple": 10}
    # Test normal removal
    remove_item(inventory, "apple", 5)
    assert inventory["apple"] == 5
    print("test_remove_item (normal) passed")

    # Test remove to zero
    remove_item(inventory, "apple", 5)
    assert "apple" not in inventory
    print("test_remove_item (to zero) passed")

    # Test KeyError
    try:
        remove_item(inventory, "orange", 1)
    except KeyError:
        print("test_remove_item (KeyError) passed")
    else:
        print("test_remove_item (KeyError) FAILED")

    # Test ValueError for more than current quantity
    inventory = {"apple": 5}
    try:
        remove_item(inventory, "apple", 10)
    except ValueError:
        print("test_remove_item (ValueError) passed")
    else:
        print("test_remove_item (ValueError) FAILED")

def test_total_value():
    inventory = {"apple": 10, "banana": 5}
    prices = {"apple": 1.0} # banana is missing
    # Should count banana as 0 price: 10 * 1.0 + 5 * 0 = 10.0
    val = total_value(inventory, prices)
    assert val == 10.0
    print("test_total_value (missing price) passed")

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("All tests passed!")
    except Exception as e:
        print(f"A test failed with error: {e}")
        import traceback
        traceback.print_exc()
