# solution.py

from collections import OrderedDict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.
    """

    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a fixed positive capacity.

        :param capacity: Maximum number of key-value pairs the cache can hold.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with `key` from the cache.

        If the key exists, it is marked as most recently used.
        Returns -1 if the key is not present.

        :param key: Integer key to look up.
        :return: Value associated with the key or -1 if absent.
        """
        if key not in self.cache:
            return -1
        # Move the accessed key to the end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def put(self, key: int, value: int) -> None:
        """
        Insert or update a key-value pair in the cache.

        If the key already exists, its value is updated and it becomes most recently used.
        If inserting a new key when at capacity, evicts the least recently used item first.

        :param key: Integer key to insert/update.
        :param value: Integer value associated with the key.
        """
        if key in self.cache:
            # Update existing key and mark as most recent
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used item (first item in OrderedDict)
            self.cache.popitem(last=False)

        # Insert the new or updated key at the end (most recent)
        self.cache[key] = value
