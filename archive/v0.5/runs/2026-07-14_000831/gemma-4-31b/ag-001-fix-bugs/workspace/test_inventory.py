from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv["apple"] == 5
    add_item(inv, "apple", 3)
    assert inv["apple"] == 8, f"Expected 8, got {inv['apple']}"
    try:
        add_item(inv, "banana", -1)
    except ValueError:
        pass
    else:
        print("Error: add_item should raise ValueError for qty < 0")

def test_remove_item():
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
        print("Error: remove_item should raise KeyError for unknown name")
    
    inv = {"orange": 2}
    try:
        remove_item(inv, "orange", 3)
    except ValueError:
        pass
    else:
        print("Error: remove_item should raise ValueError for qty > current quantity")

def test_total_value():
    inv = {"apple": 10, "banana": 5, "cherry": 2}
    prices = {"apple": 0.5, "banana": 0.2} # cherry is missing
    # (10 * 0.5) + (5 * 0.2) + (2 * 0) = 5.0 + 1.0 + 0 = 6.0
    val = total_value(inv, prices)
    assert val == 6.0, f"Expected 6.0, got {val}"

if __name__ == "__main__":
    try:
        test_add_item()
        test_remove_item()
        test_total_value()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
