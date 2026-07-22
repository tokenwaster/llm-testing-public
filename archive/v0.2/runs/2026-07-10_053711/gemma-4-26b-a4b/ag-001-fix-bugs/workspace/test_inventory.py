from inventory import add_item, remove_item, total_value

def test_add_item():
    inventory = {'apple': 5}
    # Test accumulation
    add_item(inventory, 'apple', 3)
    assert inventory['apple'] == 8, f"Expected 8, got {inventory['apple']}"
    
    # Test negative qty raises ValueError
    try:
        add_item(inventory, 'banana', -1)
    except ValueError:
        pass
    else:
        raise AssertionError("add_item should raise ValueError for negative qty")

    print("test_add_item passed!")

def test_remove_item():
    inventory = {'apple': 5, 'banana': 2}
    # Test normal removal
    remove_item(inventory, 'apple', 3)
    assert inventory['apple'] == 2, f"Expected 2, got {inventory['apple']}"
    
    # Test deletion when qty reaches 0
    remove_item(inventory, 'banana', 2)
    assert 'banana' not in inventory, "banana should have been deleted"

    # Test unknown name raises KeyError
    try:
        remove_item(inventory, 'orange', 1)
    except KeyError:
        pass
    else:
        raise AssertionError("remove_item should raise KeyError for unknown name")

    # Test removing more than current quantity raises ValueError
    try:
        remove_item(inventory, 'apple', 5)
    except ValueError:
        pass
    else:
        raise AssertionError("remove_item should raise ValueError if qty > inventory[name]")

    print("test_remove_item passed!")

def test_total_value():
    inventory = {'apple': 5, 'banana': 2, 'orange': 10}
    prices = {'apple': 2.0, 'banana': 1.5} # orange is missing
    # apple: 5 * 2.0 = 10.0
    # banana: 2 * 1.5 = 3.0
    # orange: 10 * 0 (missing) = 0.0
    # Total = 13.0
    expected_total = 13.0
    actual_total = total_value(inventory, prices)
    assert actual_total == expected_total, f"Expected {expected_total}, got {actual_total}"

    print("test_total_value passed!")

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("All tests passed successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
