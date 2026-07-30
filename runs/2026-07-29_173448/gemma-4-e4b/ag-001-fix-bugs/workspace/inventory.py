

def add_item(inventory, name, qty):
    if qty < 0:
        raise ValueError("Quantity must be non-negative")
    # BUG FIX: Accumulate quantity instead of overwriting
    current_qty = inventory.get(name, 0)
    inventory[name] = current_qty + qty
    return inventory


def remove_item(inventory, name, qty):
    if name not in inventory:
        raise KeyError(name)
    # Assuming qty is non-negative based on context.
    if qty < 0: # Added check for robustness, though not explicitly required
         raise ValueError("Quantity must be non-negative")

    if qty > inventory[name]:
        raise ValueError("Cannot remove more stock than available") # Improved message matching spec intent
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory


def total_value(inventory, prices):
    total = 0
    for name, qty in inventory.items():
        # BUG FIX: Use .get() with a default value (0) for missing prices
        price = prices.get(name, 0)
        total += qty * price
    return total
