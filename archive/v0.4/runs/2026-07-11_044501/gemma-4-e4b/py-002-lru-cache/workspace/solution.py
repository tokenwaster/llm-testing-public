from collections import OrderedDict

class LRUCache:
    """
    Implements a Least Recently Used Cache using OrderedDict for O(1) average time complexity.
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        # OrderedDict maintains insertion order and allows moving items to the end (MRU).
        # Key: key, Value: value
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Returns the stored value for the key, or -1 if absent. 
        Marks the key as most recently used (MRU).
        Time Complexity: O(1) average.
        """
        if key not in self.cache:
            return -1
        
        # Accessing the item moves it to the end of the OrderedDict (MRU position)
        value = self.cache[key]
        self.cache.move_to_end(key)
        return value

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        Updates mark the key as MRU. If capacity is exceeded by a new key, 
        the LRU item is evicted.
        Time Complexity: O(1) average.
        """
        # 1. Check if key exists (Update case)
        if key in self.cache:
            self.cache[key] = value
            # Mark as MRU
            self.cache.move_to_end(key)
            return

        # 2. New Key Insertion
        
        # Check capacity limit and evict LRU if necessary
        if len(self.cache) >= self.capacity:
            # popitem(last=False) removes the first item (the oldest/LRU)
            # Returns (key, value), but we only care about eviction side effect.
            self.cache.popitem(last=False)

        # Insert new item (automatically placed at MRU end)
        self.cache[key] = value
        # Since it's a new insertion, move_to_end is technically redundant but harmless.
        self.cache.move_to_end(key)

if __name__ == '__main__':
    # Example Usage and Testing (Optional, for verification)
    print("--- Testing LRUCache ---")
    lru = LRUCache(2)

    # Put 1: Cache = {1} (MRU)
    lru.put(1, 10); print(f"Put (1, 10). Current cache keys: {list(lru.cache.keys())}")

    # Put 2: Cache = {1, 2} (MRU)
    lru.put(2, 20); print(f"Put (2, 20). Current cache keys: {list(lru.cache.keys())}")

    # Get 1: Marks 1 as MRU. Cache = {2, 1} (MRU)
    print(f"Get 1: {lru.get(1)}. Current cache keys: {list(lru.cache.keys())}")

    # Put 3: Capacity reached. Evicts LRU (key 2). Cache = {1, 3} (MRU)
    lru.put(3, 30); print(f"Put (3, 30). Current cache keys: {list(lru.cache.keys())}")

    # Get 2: Absent. Returns -1. Cache remains {1, 3}
    print(f"Get 2: {lru.get(2)}. Current cache keys: {list(lru.cache.keys())}")

    # Update 1: Marks 1 as MRU. Cache = {3, 1} (MRU)
    lru.put(1, 100); print(f"Put (1, 100). Current cache keys: {list(lru.cache.keys())}")

    # Put 4: Capacity reached. Evicts LRU (key 3). Cache = {1, 4} (MRU)
    lru.put(4, 40); print(f"Put (4, 40). Current cache keys: {list(lru.cache.keys())}")

    # Get 3: Absent. Returns -1.
    print(f"Get 3: {lru.get(3)}. Current cache keys: {list(lru.cache.keys())}")
