# solution.py

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.

    Attributes:
        capacity (int): Maximum number of items the cache can hold.
        cache (dict[int, int]): Stores key-value pairs.
        order (collections.OrderedDict): Maintains access order; keys are ordered from least to most recently used.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache = {}
        # OrderedDict keeps insertion order; we will move accessed keys to the end.
        from collections import OrderedDict
        self.order = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve value associated with `key` if present in cache.

        Args:
            key (int): Key to look up.

        Returns:
            int: Value corresponding to the key or -1 if not found.
        """
        if key not in self.cache:
            return -1
        # Mark as most recently used by moving to end
        self.order.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the key-value pair in cache.

        If inserting a new key when at capacity, evicts least recently used item first.
        Updating an existing key marks it as most recently used.

        Args:
            key (int): Key to insert/update.
            value (int): Value associated with the key.
        """
        if key in self.cache:
            # Update value and mark as most recent
            self.cache[key] = value
            self.order.move_to_end(key)
            return

        # If at capacity, evict least recently used item
        if len(self.cache) >= self.capacity:
            lru_key, _ = self.order.popitem(last=False)  # pop first (least recent)
            del self.cache[lru_key]

        # Insert new key-value pair
        self.cache[key] = value
        self.order[key] = None  # Value not needed in order dict
