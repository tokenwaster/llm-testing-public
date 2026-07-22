class Node:
    """A node in the doubly linked list."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """LRU Cache implementation using a hash map and a doubly linked list."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Maps key to Node
        # Dummy head and tail nodes to simplify edge cases in the doubly linked list
        self.head = Node()  # MRU side (Most Recently Used)
        self.tail = Node()  # LRU side (Least Recently Used)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Removes a node from its current position in the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node) -> None:
        """Adds a node to the front of the list (immediately after the dummy head)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        """Returns the value of the key if it exists, otherwise returns -1."""
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move the accessed node to the front (mark as MRU)
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Inserts or updates a key-value pair in the cache."""
        if key in self.cache:
            # Update existing key and move to front
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

            # Create and insert the new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
