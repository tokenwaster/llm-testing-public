"""Quick test for total_value with missing price."""

from inventory import total_value

inv = {"apple": 5, "banana": 3}
prices = {"apple": 1.0}

try:
    result = total_value(inv, prices)
    print(f"Result: {result}")
except KeyError as e:
    print(f"KeyError raised: {e}")
