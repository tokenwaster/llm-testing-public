from inventory import add_item, remove_item, total_value

def test_add_item():
    print("Testing add_item...")
    inv = {'apple': 5}
    add_item(inv, 'apple', 3)
    assert inv['apple'] == 8, f"Expected 8, got {inv['apple']}"
    
    add_item(inv, 'banana', 2)
    assert inv['banana'] == 2, f"Expected 2, got {inv['banana']}"

    try:
        add_item(inv, 'apple', -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for negative qty")
    print("add_item passed!")

def test_remove_item():
    print("Testing remove_item...")
    inv = {'apple': 10, 'banana': 5}
    
    # Normal removal
    remove_item(inv, 'apple', 3)
    assert inv['apple'] == 7, f"Expected 7, got {inv['apple']}"
    
    # Removal to zero
    remove_item(inv, 'banana', 5)
    assert 'banana' not in inv, "Banana should have been deleted"
    
    # Remove more than available
    try:
        remove_item(inv, 'apple', 10)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for over-removal")
        
    # Unknown name
    try:
        remove_item(inv, 'orange', 1)
    except KeyError:
        pass
    else:
        raise AssertionError("Should have raised KeyError for unknown name")
    print("remove_item passed!")

def test_total_value():
    print("Testing total_value...")
    inv = {'apple': 10, 'banana': 5, 'orange': 2}
    prices = {'apple': 2.0, 'banana': 1.0} # orange is missing
    
    # 10 * 2.0 + 5 * 1.0 + 2 * 0 = 25.0
    val = total_value(inv, prices)
    assert val == 25.0, f"Expected 25.0, got {val}"
    print("total_value passed!")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
