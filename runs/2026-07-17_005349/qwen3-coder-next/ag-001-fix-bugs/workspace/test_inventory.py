"""Test script for inventory module."""

from inventory import add_item, remove_item, total_value

def test_add_item():
    print("Testing add_item...")
    
    # Test 1: Add new item
    inv = {}
    result = add_item(inv, "apple", 5)
    assert result == {"apple": 5}, f"Expected {{'apple': 5}}, got {result}"
    print("  Test 1 passed: Add new item")
    
    # Test 2: Accumulate existing item
    inv = {"apple": 3}
    result = add_item(inv, "apple", 5)
    assert result == {"apple": 8}, f"Expected {{'apple': 8}}, got {result}"
    print("  Test 2 passed: Accumulate existing item")
    
    # Test 3: qty < 0 raises ValueError
    try:
        add_item({}, "apple", -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  Test 3 passed: Negative qty raises ValueError")

def test_remove_item():
    print("\nTesting remove_item...")
    
    # Test 1: Remove existing item
    inv = {"apple": 10}
    result = remove_item(inv, "apple", 3)
    assert result == {"apple": 7}, f"Expected {{'apple': 7}}, got {result}"
    print("  Test 1 passed: Remove from existing item")
    
    # Test 2: Delete when reaching 0
    inv = {"apple": 5}
    result = remove_item(inv, "apple", 5)
    assert result == {}, f"Expected {{}}, got {result}"
    print("  Test 2 passed: Delete when reaching 0")
    
    # Test 3: Unknown name raises KeyError
    try:
        remove_item({}, "apple", 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        print("  Test 3 passed: Unknown name raises KeyError")
    
    # Test 4: Removing more than available raises ValueError
    try:
        remove_item({"apple": 5}, "apple", 10)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  Test 4 passed: Over-remove raises ValueError")

def test_total_value():
    print("\nTesting total_value...")
    
    # Test 1: Basic calculation
    inv = {"apple": 5, "banana": 3}
    prices = {"apple": 2.0, "banana": 1.5}
    result = total_value(inv, prices)
    expected = 5 * 2.0 + 3 * 1.5  # 10 + 4.5 = 14.5
    assert result == expected, f"Expected {expected}, got {result}"
    print("  Test 1 passed: Basic calculation")
    
    # Test 2: Missing item in prices counts as 0
    inv = {"apple": 5, "cherry": 2}
    prices = {"apple": 2.0}  # cherry is missing
    result = total_value(inv, prices)
    expected = 5 * 2.0 + 2 * 0  # 10 + 0 = 10.0
    assert result == expected, f"Expected {expected}, got {result}"
    print("  Test 2 passed: Missing item in prices counts as 0")

if __name__ == "__main__":
    test_add_item()
    test_remove_item()
    test_total_value()
    print("\nAll tests completed!")
