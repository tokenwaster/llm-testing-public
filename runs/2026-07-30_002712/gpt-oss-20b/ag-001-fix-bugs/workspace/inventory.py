

def add_item(inventory, name, qty):
    """Add `qty` units of `name` to the inventory.

    The function accumulates with any existing quantity.  ``qty`` must be
    non‑negative; a negative value raises :class:`ValueError`.
    Returns the updated inventory dict.
    """
    if qty < 0:
        raise ValueError("qty must be non-negative")
    # accumulate instead of overwrite
    inventory[name] = inventory.get(name, 0) + qty
    return inventory


def remove_item(inventory, name, qty):
    """Remove ``qty`` units of ``name`` from the inventory.

    Raises :class:`KeyError` if the item is unknown.  Removing more than the
    current quantity raises :class:`ValueError`.  If the resulting quantity is
    zero the key is removed.  The function returns the inventory dict.
    """
    if name not in inventory:
        raise KeyError(name)
    if qty > inventory[name]:
        raise ValueError("not enough stock")
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory


def total_value(inventory, prices):
    """Return the sum of ``quantity × price`` for all items.

    Items missing from ``prices`` contribute a value of zero instead of
    raising :class:`KeyError`.
    """
    total = 0.0
    for name, qty in inventory.items():
        price = prices.get(name, 0)
        total += qty * price
    return total
