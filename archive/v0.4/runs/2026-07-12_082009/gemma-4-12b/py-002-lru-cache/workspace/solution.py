class Node:
    """A node in a doubly linked list."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """Least Recently Used (LRU) Cache implementation."""
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a fixed positive capacity.
        Uses a hash map for O(1) lookups and a doubly linked list 
        to maintain usage order in O(1).
        """
        self.capacity = capacity
        self.cache = {}  # Maps key to Node object
        
        # Dummy head and tail nodes to simplify edge cases (insertion/deletion)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Removes a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Adds a node immediately after the dummy head (most recently used)."""
        first_node = self.head.next
        
        self.head.next = node
        node.prev = self.head
        node.next = first_node
        first_node.prev = node

    def get(self, key: int) -> int:
        """
        Returns the value of the key if it exists, otherwise -1.
        Marks the accessed key as most recently used.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front (MRU)
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates the key-value pair. 
        Updates mark the key as most recently used.
        Evicts the least recently used key if capacity is exceeded.
        """
        if key in self.cache:
            # Update existing value and move to front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Check if we need to evict the LRU item
            if len(self.cache) >= self.capacity:
                # The node before dummy tail is the least recently used
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove(lru_node)
            
            # Insert new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
