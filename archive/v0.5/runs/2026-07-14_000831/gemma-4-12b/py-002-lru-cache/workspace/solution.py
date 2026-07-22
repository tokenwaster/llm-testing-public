class Node:
    """A node for the doubly linked list."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """Least Recently Used (LRU) Cache implementation."""
    def __init__(self, capacity: int):
        """Initialize the cache with a fixed positive capacity."""
        self.capacity = capacity
        # Dictionary to store key-to-node mapping for O(1) access
        self.cache = {}
        
        # Dummy head and tail nodes to simplify linked list operations
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Remove a node from its current position in the doubly linked list."""
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def _add_to_front(self, node: Node) -> None:
        """Insert a node immediately after the dummy head (most recently used)."""
        first_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first_node
        first_node.prev = node

    def get(self, key: int) -> int:
        """Return the value of the key if it exists, otherwise return -1."""
        if key in self.cache:
            node = self.cache[key]
            # Move accessed node to the front (most recently used)
            self._remove(node)
            self._add_to_front(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """Insert or update a key-value pair in the cache."""
        if key in self.cache:
            # Update existing key's value and move to front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # If at capacity, evict the least recently used (tail.prev)
            if len(self.cache) >= self.capacity:
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove(lru_node)
            
            # Create new node and add to front
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
