import copy

from inventory import add_item, remove_item, total_value

failures = []


def check(label, fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{label}: unexpected {type(exc).__name__}: {exc}")


def check_raises(label, exc_type, fn):
    try:
        fn()
    except exc_type:
        return
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{label}: raised {type(exc).__name__} instead of {exc_type.__name__}")
        return
    failures.append(f"{label}: no {exc_type.__name__} raised")


# --- add_item -----------------------------------------------------------
def t_add_accumulates():
    inv = {}
    assert add_item(inv, "apple", 3) is inv
    assert inv == {"apple": 3}
    add_item(inv, "apple", 2)
    assert inv == {"apple": 5}, inv
    add_item(inv, "pear", 1)
    assert inv == {"apple": 5, "pear": 1}, inv


def t_add_negative():
    check_raises("add_item negative qty", ValueError, lambda: add_item({}, "x", -1))
    check_raises("add_item negative qty (existing)", ValueError,
                 lambda: add_item({"x": 5}, "x", -5))


def t_add_zero():
    inv = {"x": 2}
    add_item(inv, "x", 0)
    assert inv == {"x": 2}, inv


# --- remove_item --------------------------------------------------------
def t_remove_basic():
    inv = {"apple": 5, "pear": 1}
    assert remove_item(inv, "apple", 2) is inv
    assert inv == {"apple": 3, "pear": 1}, inv


def t_remove_to_zero_deletes_key():
    inv = {"apple": 5, "pear": 1}
    remove_item(inv, "pear", 1)
    assert inv == {"apple": 5}, inv
    remove_item(inv, "apple", 5)
    assert inv == {}, inv


def t_remove_unknown():
    check_raises("remove_item unknown name", KeyError,
                 lambda: remove_item({"a": 1}, "nope", 1))
    check_raises("remove_item from empty", KeyError,
                 lambda: remove_item({}, "a", 1))


def t_remove_too_many():
    check_raises("remove_item too many", ValueError,
                 lambda: remove_item({"a": 2}, "a", 3))
    # order matters: unknown name should raise KeyError even if qty too big
    check_raises("remove_item unknown + too many", KeyError,
                 lambda: remove_item({}, "a", 3))


def t_remove_zero_qty():
    inv = {"a": 4}
    remove_item(inv, "a", 0)
    assert inv == {"a": 4}, inv


# --- total_value --------------------------------------------------------
def t_total_value_basic():
    assert total_value({"a": 2, "b": 3}, {"a": 1.5, "b": 2}) == 9.0
    assert isinstance(total_value({"a": 2}, {"a": 3}), float)


def t_total_value_missing_price():
    assert total_value({"a": 2, "b": 3}, {"a": 1.5}) == 3.0
    assert total_value({"a": 2}, {}) == 0.0
    assert total_value({}, {"a": 1.0}) == 0.0


def t_total_value_does_not_mutate():
    inv = {"a": 2}
    prices = {"a": 1.0}
    snapshot_inv, snapshot_prices = copy.deepcopy(inv), copy.deepcopy(prices)
    total_value(inv, prices)
    assert inv == snapshot_inv and prices == snapshot_prices


for name, fn in sorted(globals().items()):
    if name.startswith("t_"):
        check(name, fn)

if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    raise SystemExit(1)
print("All tests passed.")
