from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._store = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self._store:
            return -1
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: int, value: int) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        elif len(self._store) >= self.capacity:
            self._store.popitem(last=False)
        self._store[key] = value
