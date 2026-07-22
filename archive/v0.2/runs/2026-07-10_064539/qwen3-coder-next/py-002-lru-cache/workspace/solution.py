class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.order = []  # list to track usage order (most recent at end)

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Move key to most recently used position
        self.order.remove(key)
        self.order.append(key)
        
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key and move to most recently used position
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used key (first in order list)
                lru_key = self.order.pop(0)
                del self.cache[lru_key]
            
            # Add new key-value pair and mark as most recently used
            self.cache[key] = value
            self.order.append(key)
