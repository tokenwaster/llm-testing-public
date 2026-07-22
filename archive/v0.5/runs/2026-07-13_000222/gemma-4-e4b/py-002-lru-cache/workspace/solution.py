class LRUCache:
    """
    Implements a Least Recently Used Cache using a dictionary (for O(1) lookup) 
    and a doubly linked list (for O(1) order maintenance).
    """

    # Helper Node class for the Doubly Linked List
    class _Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        
        # Dictionary mapping key -> Node object
        self.cache = {}
        
        # Initialize dummy head and tail nodes for the doubly linked list
        # Head.next is MRU, Tail.prev is LRU
        self.head = self._Node(0, 0) # Dummy node
        self.tail = self._Node(0, 0) # Dummy node
        
        self.head.next = self.tail
        self.tail.prev = self.head

    # --- Linked List Helper Methods ---

    def _remove_node(self, node):
        """Removes a given node from the list."""
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def _add_to_head(self, node):
        """Adds a given node right after the head (MRU position)."""
        # Current MRU is self.head.next
        current_mru = self.head.next
        
        # Link node between head and current MRU
        node.prev = self.head
        node.next = current_mru
        
        self.head.next = node
        current_mru.prev = node

    def _move_to_head(self, node):
        """Moves an existing node to the head (MRU)."""
        self._remove_node(node)
        self._add_to_head(node)

    # --- Public API Methods ---

    def get(self, key: int) -> int:
        """
        Returns the value associated with the key, or -1 if absent. 
        Marks the key as most recently used. O(1).
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        
        # Mark as MRU
        self._move_to_head(node)
        
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        If capacity is reached and the key is new, evicts LRU item. O(1).
        """
        if key in self.cache:
            # Case 1: Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Case 2: Insert new key
            new_node = self._Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)

            # Check capacity and evict if necessary
            if len(self.cache) > self.capacity:
                # The LRU node is the one just before the tail
                lru_node = self.tail.prev
                
                # Ensure we don't try to delete the dummy head itself
                if lru_node == self.head:
                    return # Should not happen if capacity > 0

                # Remove from list and cache
                self._remove_node(lru_node)
                del self.cache[lru_node.key]


# Example usage (for testing, not part of the required output structure):
# lru = LRUCache(2)
# lru.put(1, 1) # Cache: {1}
# lru.put(2, 2) # Cache: {1, 2}
# print(lru.get(1)) # Returns 1. Order: [2, 1]
# lru.put(3, 3) # Evicts key 2 (LRU). Cache: {1, 3}. Order: [1, 3]
# print(lru.get(2)) # Returns -1. Order: [1, 3]
# lru.put(4, 4) # Evicts key 1 (LRU). Cache: {3, 4}. Order: [3, 4]
