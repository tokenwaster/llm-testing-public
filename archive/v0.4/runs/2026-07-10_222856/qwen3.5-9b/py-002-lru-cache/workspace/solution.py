class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        class Node:
            def __init__(self, key=None, value=None):
                self.key = key
                self.value = value
                self.prev = None
                self.next = None
        
        self.head = Node()  # Most recently used (dummy head)
        self.tail = Node()  # Least recently used (dummy tail)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node):
        """Add node right after head (most recently used position)"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list"""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _move_to_head(self, node):
        """Move an existing node to head (most recently used)"""
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            
            # Evict if capacity exceeded
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
