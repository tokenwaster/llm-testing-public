class Node:
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
        self.cache = {}  # Maps key to Node for O(1) access
        
        # Dummy head and tail nodes to simplify doubly linked list operations
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """
        Removes a node from its current position in the doubly linked list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node):
        """
        Adds a node to the front of the list (immediately after the dummy head),
        marking it as the Most Recently Used (MRU).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        """
        Returns the value of the key if it exists, otherwise returns -1.
        A successful get marks the key as most recently used.
        """
        if key in self.cache:
            node = self.cache[key]
            # Move the accessed node to the front (MRU)
            self._remove(node)
            self._add_to_front(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        Updating an existing key marks it as most recently used.
        If the cache reaches capacity, the least recently used (LRU) key is evicted.
        """
        if key in self.cache:
            # Update existing node and move to front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Check if eviction is necessary before adding a new key
            if len(self.cache) >= self.capacity:
                # The LRU node is the one immediately before the dummy tail
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove(lru_node)

            # Create and add the new node to the front
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
