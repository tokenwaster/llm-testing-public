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
        
        # Dummy nodes for head and tail to simplify edge cases in doubly linked list
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """
        Removes a node from the doubly linked list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node):
        """
        Adds a node to the front of the list (immediately after dummy head).
        This represents the Most Recently Used position.
        """
        first_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first_node
        first_node.prev = node

    def get(self, key: int) -> int:
        """
        Returns the value of the key if it exists, otherwise -1.
        Moves the accessed node to the front (MRU).
        """
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """
        Inserts or updates the value for a key. 
        If the key exists, update it and move to front.
        If the key is new and capacity is reached, evict the LRU node.
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Check if capacity is reached
            if len(self.cache) >= self.capacity:
                # Evict the Least Recently Used node (the one before dummy tail)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove(lru_node)
            
            # Insert new key-value pair
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
