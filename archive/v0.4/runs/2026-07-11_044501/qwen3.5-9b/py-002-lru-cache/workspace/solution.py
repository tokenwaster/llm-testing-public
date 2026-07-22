class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        self.head = None  # most recently used (head of doubly linked list)
        self.tail = None  # least recently used (tail of doubly linked list)

    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def _remove_node(self, node):
        """Remove a node from the doubly linked list"""
        prev = node.prev
        next = node.next

        if prev:
            prev.next = next
        else:
            self.head = next

        if next:
            next.prev = prev
        else:
            self.tail = prev

    def _add_to_head(self, node):
        """Add a node to the head (most recently used)"""
        node.next = self.head
        node.prev = None

        if self.head:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node

    def _remove_tail(self):
        """Remove and return the tail node (least recently used)"""
        if not self.tail:
            return None

        node = self.tail
        self._remove_node(node)

        # Clean up the removed node to avoid memory leaks
        del node.key
        del node.value
        del node.prev
        del node.next

        return node

    def get(self, key: int) -> int:
        """Get value for key, or -1 if not found"""
        if key in self.cache:
            node = self.cache[key]
            # Move to head (most recently used)
            self._remove_node(node)
            self._add_to_head(node)
            return node.value
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair"""
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            # Move to head (most recently used)
            self._remove_node(node)
            self._add_to_head(node)
        else:
            # Create new node
            node = self.Node(key, value)

            if len(self.cache) >= self.capacity:
                # Remove least recently used
                removed = self._remove_tail()
                if removed:
                    del self.cache[removed.key]

            # Add to head
            self._add_to_head(node)
            self.cache[key] = node
