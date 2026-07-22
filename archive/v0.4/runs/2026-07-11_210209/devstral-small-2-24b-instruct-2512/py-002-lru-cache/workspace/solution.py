class LRUCache:
    class Node:
        def __init__(self, key=0, value=0):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        # Dummy head and tail nodes to simplify edge cases
        self.head = self.Node()
        self.tail = self.Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node):
        """Remove a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_head(self, node):
        """Add a node right after the dummy head (most recently used)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # Move the accessed node to the head (most recently used)
        self._remove_node(node)
        self._add_to_head(node)
        return node.value

    def put(self, key, value) -> None:
        if key in self.cache:
            # Update existing key: remove old node and add new one at head
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict the least recently used (tail.prev)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove_node(lru_node)
            new_node = self.Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
