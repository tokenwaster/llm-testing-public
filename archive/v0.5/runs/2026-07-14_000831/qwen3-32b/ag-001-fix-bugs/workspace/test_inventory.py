import inventory

def test_add_item():
    inv = {}
    inventory.add_item(inv, 'a', 5)
    assert inv == {'a': 5}
    inventory.add_item(inv, 'a', 3)
    assert inv == {'a': 8}

def test_remove_item():
    inv = {'a': 5}
    inventory.remove_item(inv, 'a', 2)
    assert inv == {'a': 3}
    inventory.remove_item(inv, 'a', 3)
    assert inv == {}

    try:
        inventory.remove_item({}, 'b', 1)
    except KeyError:
        pass
    else:
        assert False, "Expected KeyError"

    inv = {'a': 5}
    try:
        inventory.remove_item(inv, 'a', 6)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"

    try:
        inventory.remove_item(inv, 'a', 0)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for zero qty"

def test_total_value():
    inv = {'a': 2, 'b': 3}
    prices = {'a': 1.5, 'b': 2.0}
    assert inventory.total_value(inv, prices) == 9.0
    inv = {'a': 2, 'c': 4}
    prices = {'a': 1.5}
    assert inventory.total_value(inv, prices) == 3.0

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("All tests passed.")