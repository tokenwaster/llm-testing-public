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
        self.cache = {}  # Maps key to Node
        # Dummy head and tail nodes to simplify doubly linked list operations
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """
        Removes a node from the doubly linked list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """
        Adds a node to the front of the list (immediately after the dummy head).
        """
        first_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first_node
        first_node.prev = node

    def get(self, key: int) -> int:
        """
        Returns the value of the key if it exists, otherwise returns -1.
        Marks the accessed key as most recently used.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move the node to the front (most recently used)
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates a key-value pair. 
        If the key exists, it updates the value and marks it as most recently used.
        If the key is new and capacity is reached, evicts the least recently used key.
        """
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Check if capacity is reached before adding new node
            if len(self.cache) >= self.capacity:
                # Evict the least recently used node (the one before dummy tail)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove(lru_node)
            
            # Insert new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
