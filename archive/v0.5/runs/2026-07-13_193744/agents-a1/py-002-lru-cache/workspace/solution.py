class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        
        # Dummy head and tail nodes to simplify edge cases
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Remove a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_tail(self, node):
        """Add a node just before the tail (most recently used)."""
        prev_node = self.tail.prev
        next_node = self.tail
        
        prev_node.next = node
        node.prev = prev_node
        node.next = next_node
        next_node.prev = node

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            # Move accessed node to tail (mark as most recently used)
            self._remove(node)
            self._add_to_tail(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_tail(node)
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node after head)
                lru_node = self.head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            new_node = Node(key, value)
            self._add_to_tail(new_node)
            self.cache[key] = new_node
