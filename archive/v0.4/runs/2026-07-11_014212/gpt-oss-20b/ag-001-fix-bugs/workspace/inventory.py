"""Small stock-tracking helpers."""

def add_item(inventory, name, qty):
    """Add qty units of name to the inventory.

    Accumulates with any existing quantity. Raises ValueError if qty is negative.
    Returns the updated inventory dictionary.
    """
    if qty < 0:
        raise ValueError("qty must be non-negative")
    # accumulate rather than overwrite
    inventory[name] = inventory.get(name, 0) + qty
    return inventory


def remove_item(inventory, name, qty):
    """Remove qty units of name from the inventory.

    Raises KeyError if the item is unknown. Raises ValueError if attempting to
    remove more than the current quantity. If the resulting quantity is zero,
    the key is deleted. Returns the updated inventory dictionary.
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

    Items missing from ``prices`` count as zero rather than raising an error.
    Returns a float representing the total monetary value.
    """
    total = 0.0
    for name, qty in inventory.items():
        price = prices.get(name, 0)
        total += qty * price
    return total
