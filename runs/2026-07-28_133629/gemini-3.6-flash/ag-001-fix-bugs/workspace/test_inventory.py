import pytest
from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {}
    assert add_item(inv, "apple", 5) == {"apple": 5}
    assert add_item(inv, "apple", 3) == {"apple": 8}
    assert add_item(inv, "banana", 2) == {"apple": 8, "banana": 2}

    with pytest.raises(ValueError):
        add_item(inv, "apple", -1)

def test_remove_item():
    inv = {"apple": 8, "banana": 2}
    assert remove_item(inv, "apple", 3) == {"apple": 5, "banana": 2}

    # Unknown name raises KeyError
    with pytest.raises(KeyError):
        remove_item(inv, "orange", 1)

    # Removing more than current raises ValueError
    with pytest.raises(ValueError):
        remove_item(inv, "banana", 3)

    # Removing negative quantity raises ValueError
    with pytest.raises(ValueError):
        remove_item(inv, "apple", -1)

    # Reaching 0 removes key
    assert remove_item(inv, "banana", 2) == {"apple": 5}
    assert "banana" not in inv

def test_total_value():
    inv = {"apple": 5, "banana": 2, "orange": 3}
    prices = {"apple": 1.5, "banana": 0.5}
    val = total_value(inv, prices)
    assert val == 8.5
    assert isinstance(val, float)

    # Empty inventory
    assert total_value({}, {}) == 0.0
    assert isinstance(total_value({}, {}), float)

    # All items missing from prices
    assert total_value({"a": 10}, {}) == 0.0

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
