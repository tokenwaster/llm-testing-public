class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Maps key to Node object
        
        # Initialize dummy head and tail nodes for easier list manipulation
        self.head = Node()
        self.tail = Node()
        
        # Link dummy nodes
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node: Node):
        """Insert a new node right after the dummy head."""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node):
        """Remove a specific node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_head(self, node: Node):
        """Move an existing node to the head (mark as most recently used)."""
        self._remove_node(node)
        self._add_to_head(node)

    def _pop_tail(self) -> Node:
        """Remove and return the node just before the dummy tail (LRU item)."""
        res = self.tail.prev
        self._remove_node(res)
        return res

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Key exists: update value and move to head (mark as most recently used)
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Key does not exist: create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # If capacity exceeded, evict the least recently used item (tail.prev)
            if len(self.cache) > self.capacity:
                lru_node = self._pop_tail()
                del self.cache[lru_node.key]
