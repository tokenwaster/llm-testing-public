from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a fixed positive capacity.
        """
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Return the stored value, or -1 if absent.
        A successful get marks the key as most recently used.
        """
        if key not in self.cache:
            return -1
        # Move the accessed key to the end to mark it as most recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the key with the given value.
        Updating an existing key marks it most recently used.
        If capacity is exceeded, evict the least recently used key.
        """
        if key in self.cache:
            # If key exists, move it to the end before updating
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        # If the cache exceeds capacity, remove the first item (least recently used)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
