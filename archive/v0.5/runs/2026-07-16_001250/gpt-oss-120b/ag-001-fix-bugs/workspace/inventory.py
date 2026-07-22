"""Small stock-tracking helpers."""


def add_item(inventory, name, qty):
    """Add qty units of name to the inventory.

    Accumulates with any existing quantity. Raises ValueError if qty is negative.
    Returns the (modified) inventory.
    """
    if qty < 0:
        raise ValueError("qty must be non-negative")
    # Accumulate quantity if the item already exists
    inventory[name] = inventory.get(name, 0) + qty
    return inventory


def remove_item(inventory, name, qty):
    """Remove qty units of name from the inventory.

    Raises KeyError if name is not present. Raises ValueError if qty exceeds
    the current stock. Deletes the key if the resulting quantity is zero.
    Returns the (modified) inventory.
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
    """Total value of the inventory at the given prices.

    Items missing from `prices` are treated as having a price of 0.
    """
    total = 0
    for name, qty in inventory.items():
        total += qty * prices.get(name, 0)
    return total
