class Node:
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        
        # Create dummy head and tail nodes for doubly linked list
        self.head = Node()  # Dummy head (most recently used end)
        self.tail = Node()  # Dummy tail (least recently used end)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node_to_head(self, node: Node) -> None:
        """Add node right after head (most recently used position)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: Node) -> None:
        """Remove a node from the doubly linked list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node: Node) -> None:
        """Move existing node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_node_to_head(node)
    
    def _pop_tail(self) -> Node:
        """Remove and return the node before tail (least recently used)"""
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node
    
    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            # Move to head as it's now most recently used
            self._move_to_head(node)
            return node.value
        return -1
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node_to_head(new_node)
            
            # Check if we exceed capacity
            if len(self.cache) > self.capacity:
                lru_node = self._pop_tail()
                del self.cache[lru_node.key]
