import inventory as inv


def test_add_accumulates():
    d = {}
    inv.add_item(d, "apple", 3)
    inv.add_item(d, "apple", 2)
    assert d == {"apple": 5}


def test_add_negative():
    try:
        inv.add_item({}, "x", -1)
        assert False
    except ValueError:
        pass


def test_remove():
    d = {"apple": 5}
    inv.remove_item(d, "apple", 2)
    assert d == {"apple": 3}
    inv.remove_item(d, "apple", 3)
    assert d == {}


def test_remove_unknown():
    try:
        inv.remove_item({}, "x", 1)
        assert False
    except KeyError:
        pass


def test_remove_too_many():
    try:
        inv.remove_item({"a": 1}, "a", 2)
        assert False
    except ValueError:
        pass


def test_total_value():
    d = {"a": 2, "b": 3, "c": 4}
    prices = {"a": 1.5, "b": 2.0}
    assert inv.total_value(d, prices) == 2 * 1.5 + 3 * 2.0


if __name__ == "__main__":
    test_add_accumulates()
    test_add_negative()
    test_remove()
    test_remove_unknown()
    test_remove_too_many()
    test_total_value()
    print("all ok")
