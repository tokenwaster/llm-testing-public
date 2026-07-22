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
    else: raise AssertionError('negative add not error')
    inventory.remove_item(inv,'apple',4)
    assert inv['apple']==4
    try:
        inventory.remove_item(inv,'orange',1)
    except KeyError: pass
    else: raise AssertionError('remove unknown not error')
    try:
        inventory.remove_item(inv,'apple',10)
    except ValueError: pass
    else: raise AssertionError('remove too many not error')
    inventory.remove_item(inv,'apple',4)
    assert 'apple' not in inv
    inv={'a':2,'b':3}
    prices={'a':1.5}
    val=inventory.total_value(inv,prices)
    assert abs(val- (2*1.5+3*0))<1e-9
    print('ok')
if __name__=='__main__': test()
