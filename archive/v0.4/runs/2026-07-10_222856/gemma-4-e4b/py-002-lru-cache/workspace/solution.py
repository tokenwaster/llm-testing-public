class Node:
    """Represents a key-value pair in the doubly linked list."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """
    Implements a Least Recently Used Cache using a dictionary and a doubly linked list.
    Time complexity for get and put is O(1).
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Initialize dummy head and tail nodes for the doubly linked list
        # Head is MRU side, Tail is LRU side
        self.head = Node()
        self.tail = Node()
        
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node: Node):
        """Removes a given node from the linked list."""
        p = node.prev
        n = node.next
        if p and n:
            p.next = n
            n.prev = p

    def _add_to_head(self, node: Node):
        """Adds a node right after the dummy head (making it MRU)."""
        # Current first element is self.head.next
        first_node = self.head.next
        
        # Link new node
        node.prev = self.head
        node.next = first_node
        
        # Update surrounding nodes
        self.head.next = node
        first_node.prev = node

    def get(self, key: int) -> int:
        """
        Returns the value associated with the key, or -1 if absent. 
        Marks the key as most recently used (MRU).
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
        If updating, marks it MRU. If new and capacity reached, evicts LRU.
        """
        if key in self.cache:
            # Update existing key (Update value and mark as MRU)
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_head(node)
        else:
            # New key insertion
            if len(self.cache) >= self.capacity:
                # Evict LRU item (the node just before the dummy tail)
                lru_node = self.tail.prev
                if lru_node != self.head: # Ensure list is not empty
                    self._remove_node(lru_node)
                    del self.cache[lru_node.key]

            # Create new node and insert it
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)

if __name__ == '__main__':
    # Example Usage Test (Optional, for verification)
    print("--- Testing LRUCache ---")
    lru = LRUCache(2)
    
    # Put (1, 1) -> Cache: [(1)]
    lru.put(1, 1)
    print(f"Put (1, 1). Get(1): {lru.get(1)}") # Output: 1. List order: [1]

    # Put (2, 2) -> Cache: [(2), (1)]
    lru.put(2, 2)
    print(f"Put (2, 2). Get(2): {lru.get(2)}") # Output: 2. List order: [2, 1]

    # Put (3, 3). Capacity reached. Evict LRU (key 1). Cache: [(3), (2)]
    lru.put(3, 3)
    print(f"Put (3, 3). Get(1): {lru.get(1)}") # Output: -1. Key 1 evicted.

    # Update existing key (2, 20). Cache: [(2), (3)]
    lru.put(2, 20)
    print(f"Put (2, 20). Get(2): {lru.get(2)}") # Output: 20. List order: [2, 3]

    # Put (4, 4). Capacity reached. Evict LRU (key 3). Cache: [(4), (2)]
    lru.put(4, 4)
    print(f"Put (4, 4). Get(3): {lru.get(3)}") # Output: -1. Key 3 evicted.
