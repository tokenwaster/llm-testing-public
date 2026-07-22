class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        # Dummy nodes for head (Most Recently Used) and tail (Least Recently Used)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node):
        """Inserts a node right after the head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        """Removes a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _remove_tail(self):
        """Removes the node just before the tail (LRU item)."""
        node = self.tail.prev
        self._remove_node(node)
        return node

    def _move_to_head(self, node):
        """Moves an existing node to the head (MRU position)."""
        self._remove_node(node)
        self._add_to_head(node)

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            if len(self.cache) > self.capacity:
                lru_node = self._remove_tail()
                del self.cache[lru_node.key]
