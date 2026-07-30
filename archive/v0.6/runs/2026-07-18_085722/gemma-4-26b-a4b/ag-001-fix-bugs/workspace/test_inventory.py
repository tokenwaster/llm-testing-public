from inventory import add_item, remove_item, total_value

def test_add_item():
    print("Testing add_item...")
    inv = {"apple": 5}
    # Test accumulation
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
    # Test negative qty
    try:
        add_item(inv, "banana", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for negative qty")
    print("add_item passed!")

def test_remove_item():
    print("Testing remove_item...")
    inv = {"apple": 5, "banana": 2}
    # Test removal
    remove_item(inv, "apple", 3)
    assert inv["apple"] == 2, f"Expected 2, got {inv['apple']}"
    # Test deletion when qty reaches 0
    remove_item(inv, "banana", 2)
    assert "banana" not in inv, "banana should have been deleted"
    # Test KeyError for unknown name
    try:
        remove_item(inv, "orange", 1)
    except KeyError:
        pass
    else:
        raise AssertionError("Should have raised KeyError for unknown name")
    # Test ValueError for removing too much
    try:
        remove_item(inv, "apple", 5)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for removing more than available")
    print("remove_item passed!")

def test_total_value():
    print("Testing total_value...")
    inv = {"apple": 5, "banana": 2, "orange": 10}
    prices = {"apple": 2.0, "banana": 1.5} # orange is missing
    # Expected: 5*2.0 + 2*1.5 + 10*0 = 10.0 + 3.0 + 0 = 13.0
    expected_value = 13.0
    actual_value = total_value(inv, prices)
    assert actual_value == expected_value, f"Expected {expected_value}, got {actual_value}"
    print("total_value passed!")

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
