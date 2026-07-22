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

        # Sentinel nodes to simplify boundary conditions
        self.head = Node()
        self.tail = Node()
        
        # Link sentinels
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Remove a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Add a node immediately after the head sentinel (MRU position)."""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Move accessed node to front (most recently used)
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Key exists: update value and move to front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Key does not exist: insert new node
            
            # If at capacity, evict the least recently used item (tail.prev)
            if len(self.cache) >= self.capacity:
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node to front
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
