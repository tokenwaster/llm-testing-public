from inventory import add_item, remove_item, total_value

def test_add_item():
    inventory = {'apple': 5}
    # Test accumulation
    add_item(inventory, 'apple', 3)
    assert inventory['apple'] == 8, f"Expected 8, got {inventory['apple']}"
    
    # Test negative qty
    try:
        add_item(inventory, 'banana', -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for negative qty")
    print("test_add_item passed")

def test_remove_item():
    inventory = {'apple': 5, 'banana': 2}
    # Test normal removal
    remove_item(inventory, 'apple', 3)
    assert inventory['apple'] == 2, f"Expected 2, got {inventory['apple']}"
    
    # Test deletion when qty reaches 0
    remove_item(inventory, 'banana', 2)
    assert 'banana' not in inventory, "Banana should have been deleted"
    
    # Test unknown name
    try:
        remove_item(inventory, 'orange', 1)
    except KeyError:
        pass
    else:
        raise AssertionError("Should have raised KeyError for unknown name")
        
    # Test removing more than current quantity
    try:
        remove_item(inventory, 'apple', 5)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for removing too much")
    print("test_remove_item passed")

def test_total_value():
    inventory = {'apple': 5, 'banana': 2, 'orange': 10}
    prices = {'apple': 1.0, 'banana': 2.0} # orange is missing
    # Expected: (5 * 1.0) + (2 * 2.0) + (10 * 0) = 5 + 4 + 0 = 9.0
    expected_value = 9.0
    actual_value = total_value(inventory, prices)
    assert actual_value == expected_value, f"Expected {expected_value}, got {actual_value}"
    print("test_total_value passed")

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("All tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
