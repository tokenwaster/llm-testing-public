def add_item(inventory, name, qty):
    """Add qty units of name to inventory, accumulating with existing quantity.
    Raises ValueError if qty is negative.
    Returns the inventory dict (modified in place)."""
    if qty < 0:
        raise ValueError("qty must be non-negative")
    # Accumulate quantity if name already present
    inventory[name] = inventory.get(name, 0) + qty
    return inventory


def remove_item(inventory, name, qty):
    """Remove qty units of name from inventory.
    Raises KeyError if name not present.
    Raises ValueError if qty exceeds current stock.
    Deletes the key if quantity reaches zero.
    Returns the inventory dict (modified in place)."""
    if name not in inventory:
        raise KeyError(name)
    if qty > inventory[name]:
        raise ValueError("not enough stock")
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory


def total_value(inventory, prices):
    """Calculate total value of inventory given a price mapping.
    Items missing from prices are treated as having price 0.
    Returns a float total."""
    total = 0.0
    for name, qty in inventory.items():
        price = prices.get(name, 0)
        total += qty * price
    return total
