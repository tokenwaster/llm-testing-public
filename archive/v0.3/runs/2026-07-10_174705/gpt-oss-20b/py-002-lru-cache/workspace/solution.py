# solution.py

from collections import OrderedDict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.

    Attributes:
        capacity (int): Maximum number of key-value pairs the cache can hold.
        cache (OrderedDict[int, int]): Stores keys in order of usage,
                                       with most recently used at the end.
    """

    def __init__(self, capacity: int):
        """
        Initialize the LRUCache with a fixed positive capacity.

        Args:
            capacity (int): The maximum number of items that can be stored.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with `key` from the cache.

        If the key exists, it is marked as most recently used.
        If the key does not exist, return -1.

        Args:
            key (int): The key to look up.

        Returns:
            int: The value corresponding to `key`, or -1 if not found.
        """
        if key not in self.cache:
            return -1
        # Move key to end to mark it as most recently used
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the key-value pair in the cache.

        If `key` already exists, its value is updated and it becomes most recently used.
        If inserting a new key when at capacity, evict the least recently used item first.

        Args:
            key (int): The key to insert or update.
            value (int): The value associated with the key.
        """
        if key in self.cache:
            # Update existing key and move it to end
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used item (first item in OrderedDict)
            self.cache.popitem(last=False)
        # Insert the new or updated key as most recent
        self.cache[key] = value
