from inventory import add_item, remove_item, total_value

def test_add_item():
    # Test accumulation
    inv = {'apple': 5}
    add_item(inv, 'apple', 3)
    assert inv['apple'] == 8, f"Expected 8, got {inv['apple']}"
    
    # Test new item
    add_item(inv, 'banana', 10)
    assert inv['banana'] == 10, f"Expected 10, got {inv['banana']}"
    
    # Test ValueError
    try:
        add_item(inv, 'apple', -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for negative qty")
    
    print("test_add_item passed")

def test_remove_item():
    # Test normal removal
    inv = {'apple': 10}
    remove_item(inv, 'apple', 4)
    assert inv['apple'] == 6, f"Expected 6, got {inv['apple']}"
    
    # Test removal to zero (deletion)
    remove_item(inv, 'apple', 6)
    assert 'apple' not in inv, "Apple should be deleted when qty reaches 0"
    
    # Test KeyError
    try:
        remove_item(inv, 'orange', 1)
    except KeyError:
        pass
    else:
        raise AssertionError("Should have raised KeyError for unknown item")
        
    # Test ValueError (more than current)
    inv = {'apple': 5}
    try:
        remove_item(inv, 'apple', 6)
    except ValueError:
        pass
    else:
        raise AssertionError("Should have raised ValueError for removing more than qty")
        
    print("test_remove_item passed")

def test_total_value():
    inv = {'apple': 10, 'banana': 5, 'orange': 2}
    prices = {'apple': 2.0, 'banana': 1.0} # orange is missing
    
    # 10*2.0 + 5*1.0 + 2*0 = 25.0
    val = total_value(inv, prices)
    assert val == 25.0, f"Expected 25.0, got {val}"
    
    # Test empty inventory
    assert total_value({}, prices) == 0.0
    
    # Test empty prices
    assert total_value(inv, {}) == 0.0
    
    print("test_total_value passed")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
