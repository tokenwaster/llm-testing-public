
from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {"apples": 5}
    add_item(inv, "apples", 10)
    assert inv["apples"] == 15, f"Expected 15, got {inv['apples']}"
    
    try:
        add_item(inv, "apples", -1)
        assert False, "Should have raised ValueError for negative qty"
    except ValueError:
        pass
    print("test_add_item passed")

def test_remove_item():
    inv = {"apples": 10}
    remove_item(inv, "apples", 5)
    assert inv["apples"] == 5, f"Expected 5, got {inv['apples']}"
    
    remove_item(inv, "apples", 5)
    assert "apples" not in inv, "Key should be deleted when quantity reaches 0"
    
    inv = {"apples": 5}
    try:
        remove_item(inv, "apples", 10)
        assert False, "Should have raised ValueError for removing more than exists"
    except ValueError:
        pass

    try:
        remove_item(inv, "bananas", 1)
        assert False, "Should have raised KeyError for missing item"
    except KeyError:
        pass
    print("test_remove_item passed")

def test_total_value():
    inv = {"apples": 10, "bananas": 5, "oranges": 20}
    prices = {"apples": 2.0, "bananas": 1.0} # oranges is missing
    # 10*2.0 + 5*1.0 + 20*0 = 20 + 5 = 25.0
    assert total_value(inv, prices) == 25.0, f"Expected 25.0, got {total_value(inv, prices)}"
    print("test_total_value passed")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
