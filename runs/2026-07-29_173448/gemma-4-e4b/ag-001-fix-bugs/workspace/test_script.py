
# Test script for inventory.py

from inventory import add_item, remove_item, total_value
import pytest

def test_add_item_accumulation():
    inventory = {"apples": 10}
    initial_inv = inventory.copy()
    result = add_item(inventory, "apples", 5)
    assert result == {"apples": 15}
    # Test adding new item
    result2 = add_item(inventory, "bananas", 20)
    assert result2 == {"apples": 15, "bananas": 20}

def test_add_item_negative_qty():
    inventory = {}
    with pytest.raises(ValueError):
        add_item(inventory, "test", -1)

def test_remove_item_success_and_zeroing():
    inventory = {"apples": 10}
    # Case 1: Remove partial amount
    result1 = remove_item(inventory, "apples", 3)
    assert result1 == {"apples": 7}
    # Case 2: Remove exactly the full amount (should delete key)
    result2 = remove_item(inventory, "apples", 7)
    expected = {}
    assert result2 == expected

def test_remove_item_unknown_name():
    inventory = {"apples": 10}
    with pytest.raises(KeyError):
        remove_item(inventory, "oranges", 1)

def test_remove_item_insufficient_stock():
    inventory = {"apples": 5}
    with pytest.raises(ValueError):
        remove_item(inventory, "apples", 6)

def test_total_value_basic():
    inventory = {"apples": 10, "bananas": 20}
    prices = {"apples": 1.0, "bananas": 0.5} # Total: 10*1 + 20*0.5 = 20.0
    assert total_value(inventory, prices) == 20.0

def test_total_value_missing_price():
    inventory = {"apples": 10, "grapes": 5}
    prices = {"apples": 1.0} # Grapes are missing, should count as 0 price
    # Total: 10*1 + 5*0 = 10.0
    assert total_value(inventory, prices) == 10.0

def test_total_value_no_prices():
    inventory = {"apples": 10}
    prices = {} # All items missing price
    assert total_value(inventory, prices) == 0.0

# Note: Since pytest needs to be installed or run in a specific context, I will adapt this for direct execution simulation if necessary, but first, I'll run it using standard Python features assuming the module structure is ready.
