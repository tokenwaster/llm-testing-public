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
        self.capacity = capacity
        self.cache = {}  # Maps key to Node for O(1) access
        
        # Dummy head and tail nodes to simplify edge cases in the doubly linked list
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Removes a node from its current position in the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Adds a node to the front of the list (immediately after dummy head)."""
        after_head = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = after_head
        after_head.prev = node

    def get(self, key: int) -> int:
        """Returns the value of the key if it exists, otherwise -1."""
        if key in self.cache:
            node = self.cache[key]
            # Move the accessed node to the front (most recently used)
            self._remove(node)
            self._add_to_front(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """Inserts or updates a key-value pair in the cache."""
        if key in self.cache:
            # Update existing key and move it to the front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Check if capacity is reached before adding a new key
            if len(self.cache) >= self.capacity:
                # Evict the least recently used node (the one before dummy tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Create and add the new node to the front
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
