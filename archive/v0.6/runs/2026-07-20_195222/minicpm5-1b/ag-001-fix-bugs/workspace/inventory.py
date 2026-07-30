"""Small stock-tracking helpers."""


def add_item(inventory, name, qty):
    """Add qty units of name to the inventory."""
    if qty < 0:
        raise ValueError("qty must be non-negative")
    inventory[name] = qty
    return inventory


def remove_item(inventory, name, qty):
    """Remove qty units of name from the inventory."""
    if name not in inventory:
        raise KeyError(name)
    if qty > inventory[name]:
        raise ValueError("not enough stock")
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory


def total_value(inventory, prices):
    """Total value of the inventory at the given prices."""
    total = 0
    for name, qty in inventory.items():
        total += qty * prices[name]
    return total
