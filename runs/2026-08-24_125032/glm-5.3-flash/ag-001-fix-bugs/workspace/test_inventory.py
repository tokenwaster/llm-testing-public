"""Quick sanity tests for inventory.py against the specification."""
import inventory


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"PASS: {msg}")


def expect_raises(exc_type, fn, *args, msg=""):
    try:
        fn(*args)
    except exc_type:
        print(f"PASS: raised {exc_type.__name__} {msg}")
        return
    except Exception as e:  # noqa: BLE001
        raise AssertionError(
            f"FAIL{msg}: expected {exc_type.__name__}, got {type(e).__name__}: {e}"
        )
    raise AssertionError(f"FAIL{msg}: expected {exc_type.__name__}, nothing raised")


# --- add_item ---
inv = {}
assert inventory.add_item(inv, "apple", 3) is inv
check(inv == {"apple": 3}, "add_item adds new item")
inventory.add_item(inv, "apple", 2)
check(inv == {"apple": 5}, "add_item accumulates existing quantity")
inventory.add_item(inv, "pear", 0)
check(inv == {"apple": 5, "pear": 0}, "add_item accepts qty == 0")
expect_raises(ValueError, inventory.add_item, inv, "x", -1, msg="(negative qty)")

# --- remove_item ---
inv = {"apple": 5}
assert inventory.remove_item(inv, "apple", 2) is inv
check(inv == {"apple": 3}, "remove_item subtracts")
inventory.remove_item(inv, "apple", 3)
check(inv == {}, "remove_item deletes key at exactly 0")
expect_raises(KeyError, inventory.remove_item, inv, "ghost", 1, msg="(unknown item)")
inv = {"apple": 2}
expect_raises(ValueError, inventory.remove_item, inv, "apple", 3,
              msg="(removing more than available)")
check(inv == {"apple": 2}, "inventory unchanged after failed removal")

# --- total_value ---
inv = {"apple": 3, "pear": 2, "plum": 4}
val = inventory.total_value(inv, {"apple": 1.5, "pear": 2})
check(abs(val - (3 * 1.5 + 2 * 2)) < 1e-9, f"total_value sums correctly ({val})")
check(isinstance(val, float), "total_value returns a float")
val2 = inventory.total_value({}, {})
check(val2 == 0.0, "total_value on empty inventory")

print("\nAll checks passed.")
