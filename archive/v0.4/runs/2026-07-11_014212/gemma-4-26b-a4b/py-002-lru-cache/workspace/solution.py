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
        Insert or update the key-value pair. 
        Updating an existing key marks it most recently used.
        When inserting a new key at capacity, evict the least recently used key first.
        """
        if key in self.cache:
            # Move existing key to the end before updating its value
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        # If capacity is exceeded, remove the first item (the least recently used)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
