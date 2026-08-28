from inventory import add_item, remove_item, total_value

def test_add():
    inv = {}
    add_item(inv, 'apple', 5)
    assert inv == {'apple':5}, inv
    add_item(inv, 'apple', 3)
    assert inv == {'apple':8}, inv
    add_item(inv, 'banana', 2)
    assert inv == {'apple':8,'banana':2}, inv
    try:
        add_item(inv, 'apple', -1)
        assert False, "should raise"
    except ValueError:
        pass
    print("add_item ok")

def test_remove():
    inv = {'apple':5,'banana':2}
    remove_item(inv, 'apple', 2)
    assert inv == {'apple':3,'banana':2}
    remove_item(inv, 'banana',2)
    assert inv == {'apple':3}
    try:
        remove_item(inv, 'orange',1)
        assert False
    except KeyError:
        pass
    try:
        remove_item(inv, 'apple',10)
        assert False
    except ValueError:
        pass
    print("remove_item ok")

def test_total():
    inv = {'apple':3,'banana':2,'cherry':5}
    prices = {'apple':1.5,'banana':0.5}
    val = total_value(inv, prices)
    # cherry missing -> 0
    expected = 3*1.5 + 2*0.5
    assert abs(val - expected) < 1e-9, val
    assert isinstance(val, float), type(val)
    print("total_value ok")

test_add()
test_remove()
test_total()
print("All tests passed")
