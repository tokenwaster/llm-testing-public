class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        class Node:
            def __init__(self, key=0, value=0):
                self.key = key
                self.value = value
                self.prev = None
                self.next = None
        
        self.head = None  # Most recently used
        self.tail = None  # Least recently used
    
    def _add_to_head(self, node):
        """Add node to the head (MRU position)"""
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list"""
        if node.prev:
            node.prev.next = node.next
        else:
            self.tail = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self.head = node.prev
    
    def _move_to_head(self, node):
        """Move a node to the head (MRU position)"""
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
            
            # If capacity exceeded, remove LRU (tail)
            if len(self.cache) > self.capacity:
                lru_node = self.tail
                del self.cache[lru_node.key]
                self._remove_node(lru_node)
