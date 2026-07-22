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
        
        # Dummy head and tail nodes to simplify boundary checks
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node):
        """Add node right after the dummy head."""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        """Remove a specific node from the list."""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_head(self, node):
        """Move an existing node to the head (mark as most recently used)."""
        self._remove_node(node)
        self._add_to_head(node)

    def _pop_tail(self):
        """Remove and return the node just before the dummy tail."""
        res = self.tail.prev
        self._remove_node(res)
        return res

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Mark as recently used by moving to head
        self._move_to_head(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Key exists: update value and move to head
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # New key: create node, add to cache and list
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # If capacity exceeded, evict the least recently used item (before tail)
            if len(self.cache) > self.capacity:
                lru_node = self._pop_tail()
                del self.cache[lru_node.key]
