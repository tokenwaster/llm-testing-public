from inventory import add_item, remove_item, total_value

def test():
    inv={}
    add_item(inv,'apple',5)
    assert inv['apple']==5
    add_item(inv,'apple',3)
    assert inv['apple']==8
    try:
        add_item(inv,'banana',-1)
    except ValueError: pass
    else: raise AssertionError('negative qty not error')
    remove_item(inv,'apple',2)
    assert inv['apple']==6
    try:
        remove_item(inv,'orange',1)
    except KeyError: pass
    else: raise AssertionError('unknown key no error')
    try:
        remove_item(inv,'apple',10)
    except ValueError: pass
    else: raise AssertionError('remove too many not error')
    remove_item(inv,'apple',6)
    assert 'apple' not in inv
    inv={'pear':4}
    prices={'pear':2.5,'banana':1.0}
    assert total_value(inv,prices)==10.0
    inv['orange']=3
    assert total_value(inv,prices)==10.0  # orange price missing -> 0

if __name__=='__main__':
    test()
    print('ok')
