# solution.py

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for get and put operations.

    Attributes:
        capacity (int): Maximum number of items the cache can hold.
        cache (dict[int, int]): Stores key-value pairs.
        order (collections.OrderedDict): Maintains usage order; keys are ordered from least to most recently used.
    """

    def __init__(self, capacity: int):
        """
        Initialize the LRUCache with a given positive capacity.

        Args:
            capacity (int): The maximum number of items the cache can store.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache = {}
        # OrderedDict to keep track of usage order: first item is LRU, last is MRU
        from collections import OrderedDict
        self.order = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with the given key.

        If the key exists, it becomes the most recently used.
        Returns -1 if the key is not present.

        Args:
            key (int): The key to look up.

        Returns:
            int: The value corresponding to the key or -1 if absent.
        """
        if key not in self.cache:
            return -1
        # Move key to end to mark as most recently used
        self.order.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the key-value pair in the cache.

        If the key already exists, its value is updated and it becomes most recently used.
        If inserting a new key when at capacity, evicts the least recently used item first.

        Args:
            key (int): The key to insert/update.
            value (int): The value associated with the key.
        """
        if key in self.cache:
            # Update value and mark as most recent
            self.cache[key] = value
            self.order.move_to_end(key)
            return

        # If at capacity, evict least recently used item
        if len(self.cache) >= self.capacity:
            lru_key, _ = self.order.popitem(last=False)  # pop first (LRU)
            del self.cache[lru_key]

        # Insert new key-value pair
        self.cache[key] = value
        self.order[key] = None  # Value in order dict is irrelevant
