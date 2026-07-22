class Node:
    """Helper class for the Doubly Linked List."""
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """
    Implements a Least Recently Used Cache using a dictionary and a Doubly Linked List 
    to ensure O(1) time complexity for get and put operations.
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self.capacity = capacity
        # Dictionary maps key -> Node object
        self.cache = {}
        
        # Initialize dummy head and tail nodes for the DLL
        # Head (MRU side) <-> ... <-> Tail (LRU side)
        self.head = Node()
        self.tail = Node()
        
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node: Node):
        """Removes a given node from the list."""
        if node.prev and node.next:
            p = node.prev
            n = node.next
            p.next = n
            n.prev = p

    def _add_to_head(self, node: Node):
        """Adds a given node right after the dummy head (MRU position)."""
        # Current MRU node is self.head.next
        old_mru = self.head.next
        
        # Link new node between head and old MRU
        node.prev = self.head
        node.next = old_mru
        
        self.head.next = node
        old_mru.prev = node

    def get(self, key: int) -> int:
        """
        Returns the stored value for the key, or -1 if absent. 
        Marks the key as most recently used. O(1).
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        
        # Mark as MRU by moving it to the head
        self._remove_node(node)
        self._add_to_head(node)
        
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        Marks the key as most recently used. Evicts LRU if capacity is reached. O(1).
        """
        if key in self.cache:
            # Case 1: Update existing key (and mark MRU)
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_head(node)
        else:
            # Case 2: Insert new key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)

            # Check capacity and evict LRU if necessary
            if len(self.cache) > self.capacity:
                # The node just before the dummy tail is the LRU element
                lru_node = self.tail.prev
                
                # Evict it
                self._remove_node(lru_node)
                del self.cache[lru_node.key]

if __name__ == '__main__':
    # Example Usage Test (Optional, for verification)
    print("--- Testing LRUCache ---")
    cache = LRUCache(2)
    
    # put(1, 1) -> Cache: {1} [MRU]
    cache.put(1, 1)
    
    # put(2, 2) -> Cache: {2, 1} [MRU, LRU]
    cache.put(2, 2)
    
    print(f"Get(1): {cache.get(1)}") # Returns 1. Marks 1 as MRU. Cache: {1, 2} [MRU, LRU]
    
    # put(3, 3). Capacity=2. Evicts LRU (key 2). Cache: {3, 1} [MRU, LRU]
    cache.put(3, 3)
    
    print(f"Get(2): {cache.get(2)}") # Returns -1. Key 2 was evicted.
    
    # put(4, 4). Capacity=2. Evicts LRU (key 1). Cache: {4, 3} [MRU, LRU]
    cache.put(4, 4)

    print(f"Get(3): {cache.get(3)}") # Returns 3. Marks 3 as MRU. Cache: {3, 4} [MRU, LRU]
