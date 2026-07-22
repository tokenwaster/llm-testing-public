import inventory

def test():
    inv={}
    inventory.add_item(inv,'apple',5)
    assert inv['apple']==5
    inventory.add_item(inv,'apple',3)
    assert inv['apple']==8
    try:
        inventory.add_item(inv,'banana',-1)
    except ValueError: pass
    else: raise AssertionError('negative not error')
    inventory.remove_item(inv,'apple',4)
    assert inv['apple']==4
    try:
        inventory.remove_item(inv,'orange',1)
    except KeyError: pass
    else: raise AssertionError('missing key not error')
    try:
        inventory.remove_item(inv,'apple',10)
    except ValueError: pass
    else: raise AssertionError('over remove not error')
    inventory.remove_item(inv,'apple',4)
    assert 'apple' not in inv
    inv={'pear':2}
    prices={'pear':1.5,'banana':0.5}
    total=inventory.total_value(inv,prices)
    assert total==3.0
    # missing price
    inv={'orange':4}
    total=inventory.total_value(inv,{'apple':1})
    assert total==0
    print('ok')
if __name__=='__main__': test()
