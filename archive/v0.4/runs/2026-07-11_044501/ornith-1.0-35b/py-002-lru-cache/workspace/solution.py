class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Maps key -> Node
        
        # Sentinel nodes for head and tail to simplify boundary conditions
        self.head = Node()
        self.tail = Node()
        
        # Link sentinels
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key's value and move to front (most recently used)
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Insert new key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
            
            if len(self.cache) > self.capacity:
                # Evict the least recently used item (node right before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]

    def _add_to_front(self, node):
        """Insert node immediately after head."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        """Remove a specific node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_front(self, node):
        """Move an existing node to the front (most recently used position)."""
        self._remove_node(node)
        self._add_to_front(node)
