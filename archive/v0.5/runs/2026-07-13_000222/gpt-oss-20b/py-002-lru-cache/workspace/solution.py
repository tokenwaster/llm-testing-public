# solution.py

class ListNode:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation with O(1) average time complexity
    for get and put operations.

    Uses a combination of a doubly linked list to maintain usage order and a hash map
    for fast key-to-node lookup.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = {}  # key -> ListNode

        # Dummy head and tail nodes to simplify edge cases
        self.head = ListNode()
        self.tail = ListNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_node(self, node: ListNode) -> None:
        """Insert node right after head (most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: ListNode) -> None:
        """Detach node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_front(self, node: ListNode) -> None:
        """Move an existing node to the front (most recently used)."""
        self._remove_node(node)
        self._add_node(node)

    def _evict_lru(self) -> None:
        """
        Remove the least recently used node (node before tail).
        Assumes that at least one node exists.
        """
        lru = self.tail.prev
        self._remove_node(lru)
        del self.cache[lru.key]

    def get(self, key: int) -> int:
        """Return value associated with key or -1 if not present."""
        node = self.cache.get(key)
        if node is None:
            return -1
        # Mark as most recently used
        self._move_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update the key-value pair."""
        node = self.cache.get(key)

        if node:
            # Update existing value and move to front
            node.value = value
            self._move_to_front(node)
        else:
            # Insert new node
            if len(self.cache) >= self.capacity:
                self._evict_lru()
            new_node = ListNode(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
