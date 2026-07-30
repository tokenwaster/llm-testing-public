from inventory import add_item, remove_item, total_value

def test_add_item():
    print("Testing add_item...")
    inv = {"apple": 5}
    # Test accumulation
    res = add_item(inv, "apple", 3)
    assert res["apple"] == 8, f"Expected 8, got {res['apple']}"
    
    # Test negative qty raises ValueError
    try:
        add_item(inv, "banana", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("add_item should raise ValueError for negative qty")
    print("add_item passed!")

def test_remove_item():
    print("Testing remove_item...")
    inv = {"apple": 5, "banana": 2}
    # Test normal removal
    res = remove_item(inv, "apple", 3)
    assert res["apple"] == 2
    
    # Test deletion if qty becomes 0
    res = remove_item(inv, "banana", 2)
    assert "banana" not in res
    
    # Test unknown name raises KeyError
    try:
        remove_item(inv, "orange", 1)
    except KeyError:
        pass
    else:
        raise AssertionError("remove_item should raise KeyError for unknown name")
        
    # Test removing more than current quantity raises ValueError
    try:
        remove_item(inv, "apple", 5)
    except ValueError:
        pass
    else:
        raise AssertionError("remove_item should raise ValueError if qty > inventory[name]")
    print("remove_item passed!")

def test_total_value():
    print("Testing total_value...")
    inv = {"apple": 5, "banana": 2, "orange": 3}
    prices = {"apple": 10, "banana": 5} # orange is missing
    # Spec: Items missing from prices count as 0
    # Expected: (5 * 10) + (2 * 5) + (3 * 0) = 50 + 10 + 0 = 60
    res = total_value(inv, prices)
    assert res == 60.0, f"Expected 60.0, got {res}"
    print("total_value passed!")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed successfully!")
