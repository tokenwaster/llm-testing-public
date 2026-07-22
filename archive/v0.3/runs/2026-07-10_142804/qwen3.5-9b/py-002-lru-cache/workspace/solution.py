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
        
        # Doubly linked list with sentinels
        self.head = Node()  # Most recently used
        self.tail = Node()  # Least recently used
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node):
        """Add a node right after head (most recently used position)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the linked list"""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _move_to_head(self, node):
        """Move an existing node to head (mark as most recently used)"""
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
            self._add_to_head(node)
            self.cache[key] = node
            
            # If capacity exceeded, remove least recently used (tail.prev)
            if len(self.cache) > self.capacity:
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
