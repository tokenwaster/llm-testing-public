from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {}
    add_item(inv, "apple", 5)
    assert inv == {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}, f"Expected {{'apple': 8}}, got {inv}"
    try:
        add_item(inv, "banana", -1)
    except ValueError:
        pass
    else:
        print("Failed to raise ValueError for negative qty in add_item")

def test_remove_item():
    inv = {"apple": 8}
    remove_item(inv, "apple", 3)
    assert inv == {"apple": 5}
    remove_item(inv, "apple", 5)
    assert inv == {}, f"Expected {{}}, got {inv}"
    try:
        remove_item(inv, "banana", 1)
    except KeyError:
        pass
    else:
        print("Failed to raise KeyError for unknown item in remove_item")
    
    inv = {"apple": 5}
    try:
        remove_item(inv, "apple", 6)
    except ValueError:
        pass
    else:
        print("Failed to raise ValueError for removing more than available stock in remove_item")

def test_total_value():
    inv = {"apple": 10, "banana": 5, "cherry": 2}
    prices = {"apple": 0.5, "banana": 0.2} # cherry missing
    # (10 * 0.5) + (5 * 0.2) + (2 * 0) = 5.0 + 1.0 + 0 = 6.0
    val = total_value(inv, prices)
    assert val == 6.0, f"Expected 6.0, got {val}"

if __name__ == "__main__":
    try:
        test_add_item()
        print("test_add_item passed")
        test_remove_item()
        print("test_remove_item passed")
        test_total_value()
        print("test_total_value passed")
        print("All tests passed!")
    except AssertionError as e:
        print(f"Assertion failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
