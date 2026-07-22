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
        Return the value of the key if it exists in the cache, otherwise return -1.
        A successful get marks the key as most recently used.
        """
        if key not in self.cache:
            return -1
        
        # Move the accessed key to the end to mark it as most recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert or update the value of the key. 
        Updating an existing key marks it as most recently used.
        If inserting a new key exceeds capacity, evict the least recently used item.
        """
        if key in self.cache:
            # Move to end before updating to mark as most recently used
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        # If capacity is exceeded, remove the first item (the least recently used)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
