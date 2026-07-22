def add_item(inventory, name, qty):
    if qty < 0:
        raise ValueError("qty must be non-negative")
    inventory[name] = inventory.get(name, 0) + qty
    return inventory

def remove_item(inventory, name, qty):
    if name not in inventory:
        raise KeyError(name)
    if qty < 0:
        raise ValueError("qty must be non-negative")
    if qty > inventory[name]:
        raise ValueError("not enough stock")
    inventory[name] -= qty
    if inventory[name] == 0:
        del inventory[name]
    return inventory

def total_value(inventory, prices):
    total = 0.0
    for name, qty in inventory.items():
        total += qty * prices.get(name, 0)
    return total