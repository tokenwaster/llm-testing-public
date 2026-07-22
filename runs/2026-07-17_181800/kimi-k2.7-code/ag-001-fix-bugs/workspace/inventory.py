"""Small stock-tracking module."""


def add_item(inventory: dict, name: str, qty: int) -> dict:
    """Add qty units of name to inventory, accumulating with existing quantity."""
    if qty < 0:
        raise ValueError("qty must be non-negative")
    inventory[name] = inventory.get(name, 0) + qty
    return inventory


def remove_item(inventory: dict, name: str, qty: int) -> dict:
    """Remove qty units of name from inventory."""
    if name not in inventory:
        raise KeyError(name)
    if qty < 0:
        raise ValueError("qty must be non-negative")
    if qty > inventory[name]:
        raise ValueError("cannot remove more than present")
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory


def total_value(inventory: dict, prices: dict) -> float:
    """Return total value of inventory using provided prices.

    Items missing from prices count as 0.
    """
    return sum(inventory[name] * prices.get(name, 0) for name in inventory)
