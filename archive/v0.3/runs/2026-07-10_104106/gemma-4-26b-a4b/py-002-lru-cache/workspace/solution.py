class Node:
    """A node in the doubly linked list."""
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a fixed positive capacity.
        """
        self.capacity = capacity
        self.cache = {}  # Maps key to Node in the doubly linked list
        
        # Dummy nodes to simplify boundary conditions (head and tail)
        # head.next will be the Least Recently Used (LRU) node
        # tail.prev will be the Most Recently Used (MRU) node
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """Removes a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_mru(self, node: Node):
        """Adds a node to the end of the list (just before the dummy tail)."""
        last_node = self.tail.prev
        last_node.next = node
        node.prev = last_node
        node.next = self.tail
        self.tail.prev = node

    def get(self, key: int) -> int:
        """
        Returns the value of the key if it exists, otherwise returns -1.
        A successful get marks the key as most recently used.
        """
        if key in self.cache:
            node = self.cache[key]
            # Move the accessed node to the MRU position
            self._remove(node)
            self._add_to_mru(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates the value for the given key. 
        If the key already exists, its value is updated and it becomes MRU.
        If a new key is inserted and capacity is reached, the LRU key is evicted.
        """
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_mru(node)
        else:
            # Check if eviction is necessary
            if len(self.cache) >= self.capacity:
                # The LRU node is the one immediately after the dummy head
                lru_node = self.head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Create and add the new node to MRU position
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_mru(new_node)
