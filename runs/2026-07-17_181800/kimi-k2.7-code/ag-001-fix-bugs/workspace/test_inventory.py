from inventory import add_item, remove_item, total_value


def test_add_item():
    inv = {}
    assert add_item(inv, "apple", 5) is inv
    assert inv == {"apple": 5}
    add_item(inv, "apple", 3)
    assert inv == {"apple": 8}
    try:
        add_item(inv, "apple", -1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_remove_item():
    inv = {"apple": 5, "banana": 2}
    assert remove_item(inv, "apple", 3) is inv
    assert inv == {"apple": 2, "banana": 2}
    remove_item(inv, "apple", 2)
    assert inv == {"banana": 2}
    try:
        remove_item(inv, "apple", 1)
        assert False, "expected KeyError"
    except KeyError:
        pass
    try:
        remove_item(inv, "banana", 5)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_total_value():
    inv = {"apple": 5, "banana": 2, "orange": 3}
    prices = {"apple": 1.0, "banana": 0.5}
    assert total_value(inv, prices) == 5 * 1.0 + 2 * 0.5 + 3 * 0


if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("all tests passed")
