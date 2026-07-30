from inventory import add_item, remove_item, total_value

def main():
    inv = {}
    
    # Test add_item accumulates
    assert add_item(inv, 'apple', 5) is inv
    assert add_item(inv, 'apple', 3) == {'apple': 8}
    print("PASS: add_item accumulates")
    
    # Test add_item rejects negative
    try:
        add_item(inv, 'banana', -1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("PASS: add_item rejects negative qty")
    
    # Test remove_item removes quantity
    assert remove_item(inv, 'apple', 2) == {'apple': 6}
    print("PASS: remove_item reduces quantity")
    
    # Test remove_item deletes at zero
    inv = {}
    add_item(inv, 'cherry', 4)
    assert remove_item(inv, 'cherry', 4) == {}
    print("PASS: remove_item deletes key at zero")
    
    # Test remove_item raises KeyError for unknown name
    try:
        remove_item({}, 'nope', 1)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    print("PASS: remove_item raises KeyError for unknown name")
    
    # Test remove_item raises ValueError when removing more than available
    add_item(inv, 'date', 3)
    try:
        remove_item(inv, 'date', 5)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("PASS: remove_item raises ValueError for over-removal")
    
    # Test total_value with missing prices (should be 0)
    inv = {'apple': 10, 'banana': 5}
    assert total_value(inv, {'apple': 2.0}) == 20.0
    print("PASS: total_value treats missing price as 0")
    
    # Test total_value normal case
    assert total_value({'a': 3, 'b': 7}, {'a': 1.5, 'b': 2.0}) == 21.0
    print("PASS: total_value sums correctly")

if __name__ == '__main__':
    main()
