from collections import OrderedDict

class LRUCache:
    """
    Implements a Least Recently Used Cache using OrderedDict for O(1) average time complexity 
    for both get and put operations.
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        # Using OrderedDict: keys are stored in order of usage.
        # The beginning (popitem(last=False)) is LRU.
        # The end (move_to_end) is MRU.
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Returns the stored value for the key, or -1 if absent. 
        Marks the key as most recently used. O(1).
        """
        if key not in self.cache:
            return -1
        
        # Mark as MRU by moving it to the end of the ordered dictionary
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        Marks it as MRU. Evicts LRU if capacity is reached for new keys. O(1).
        """
        if self.capacity == 0:
            return

        # Case 1: Key exists (Update)
        if key in self.cache:
            # Update value and mark as MRU
            self.cache[key] = value
            self.cache.move_to_end(key)
            return

        # Case 2: New Key Insertion
        
        # Check for capacity limit (only evict if we are adding a new key)
        if len(self.cache) >= self.capacity:
            # Evict the LRU item (the first item inserted/used, popped from the left)
            # popitem(last=False) removes and returns the (key, value) pair that was least recently used.
            self.cache.popitem(last=False)

        # Insert new key-value pair (automatically placed at the MRU end)
        self.cache[key] = value
