Your workspace contains `inventory.py`, a small stock-tracking module that does
not fully match its specification. Find and fix the bugs. Do not rename functions
or change their signatures.

Specification:

- `add_item(inventory: dict, name: str, qty: int) -> dict`
  Adds `qty` units of `name` to the inventory dict, **accumulating** with any
  existing quantity. `qty < 0` raises `ValueError`. Returns the inventory.
- `remove_item(inventory: dict, name: str, qty: int) -> dict`
  Removes `qty` units. Unknown `name` raises `KeyError`. Removing more than the
  current quantity raises `ValueError`. If the quantity reaches exactly 0 the key
  is deleted. Returns the inventory.
- `total_value(inventory: dict, prices: dict) -> float`
  Sum of `quantity × price` over all items. Items **missing from `prices` count
  as 0** rather than raising.

Inspect the code, write a quick test script if you like, run it, and fix
`inventory.py` in place until it matches the spec.
