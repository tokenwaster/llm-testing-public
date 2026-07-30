from inventory import add_item, remove_item, total_value

def test_add_item():
    print("Testing add_item...")
    inv = {}
    add_item(inv, "apple", 5)
    assert inv["apple"] == 5
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
    try:
        add_item(inv, "apple", -1)
    except ValueError:
        pass
    else:
        print("Fail: add_item should raise ValueError for negative qty")
    print("add_item passed!")

def test_remove_item():
    print("Testing remove_item...")
    inv = {"apple": 8}
    remove_item(inv, "apple", 3)
    assert inv["apple"] == 5
    remove_item(inv, "apple", 5)
    assert "apple" not in inv
    try:
        remove_item(inv, "banana", 1)
    except KeyError:
        pass
    else:
        print("Fail: remove_item should raise KeyError for missing item")
    
    inv = {"orange": 5}
    try:
        remove_item(inv, "orange", 6)
    except ValueError:
        pass
    else:
        print("Fail: remove_item should raise ValueError for excessive removal")
    print("remove_item passed!")

def test_total_value():
    print("Testing total_value...")
    inv = {"apple": 10, "banana": 5}
    prices = {"apple": 2.0} # banana is missing
    val = total_value(inv, prices)
    assert val == 20.0, f"Expected 20.0, got {val}"
    print("total_value passed!")

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        raise e
