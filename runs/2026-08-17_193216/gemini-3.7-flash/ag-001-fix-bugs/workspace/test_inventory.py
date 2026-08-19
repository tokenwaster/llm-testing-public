import pytest
from inventory import add_item, remove_item, total_value

def test_add_item():
    inv = {}
    res = add_item(inv, "apple", 5)
    assert res is inv
    assert inv == {"apple": 5}

    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}

    add_item(inv, "banana", 2)
    assert inv == {"apple": 8, "banana": 2}

    add_item(inv, "orange", 0)
    assert inv == {"apple": 8, "banana": 2, "orange": 0}

    try:
        add_item(inv, "apple", -1)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_remove_item():
    inv = {"apple": 5, "banana": 2}
    res = remove_item(inv, "apple", 2)
    assert res is inv
    assert inv == {"apple": 3, "banana": 2}

    # Exactly 0 deletes key
    remove_item(inv, "apple", 3)
    assert "apple" not in inv
    assert inv == {"banana": 2}

    # Unknown item raises KeyError
    try:
        remove_item(inv, "apple", 1)
        assert False, "Should raise KeyError"
    except KeyError:
        pass

    # Removing more than current quantity raises ValueError
    try:
        remove_item(inv, "banana", 3)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

    # Removing negative quantity raises ValueError
    try:
        remove_item(inv, "banana", -1)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_total_value():
    inv = {"apple": 2, "banana": 3, "orange": 1}
    prices = {"apple": 1.5, "banana": 2.0} # orange is missing
    assert total_value(inv, prices) == 9.0

    assert total_value({}, {}) == 0.0
    assert total_value({"apple": 5}, {}) == 0.0
    assert total_value({}, {"apple": 10.0}) == 0.0

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed!")
