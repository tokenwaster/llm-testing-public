from solution import LRUCache


def test_basic_put_get():
    c = LRUCache(2)
    c.put(1, 10)
    assert c.get(1) == 10


def test_missing_returns_minus_one():
    c = LRUCache(2)
    assert c.get(99) == -1


def test_eviction_order():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.put(3, 30)          # evicts 1
    assert c.get(1) == -1
    assert c.get(2) == 20
    assert c.get(3) == 30


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.get(1)              # 1 is now most recent
    c.put(3, 30)          # evicts 2
    assert c.get(1) == 10
    assert c.get(2) == -1


def test_update_refreshes_recency():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.put(1, 11)          # update, 1 most recent
    c.put(3, 30)          # evicts 2
    assert c.get(1) == 11
    assert c.get(2) == -1
    assert c.get(3) == 30


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 10)
    c.put(2, 20)
    assert c.get(1) == -1
    assert c.get(2) == 20
