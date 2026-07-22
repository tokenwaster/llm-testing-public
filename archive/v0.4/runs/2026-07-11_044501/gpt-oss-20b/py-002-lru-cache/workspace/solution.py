# solution.py

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with O(1) average time complexity
    for both `get` and `put` operations.

    Uses a combination of a dictionary for fast key lookup and a doubly linked list
    to maintain the order of usage. The head of the list represents the most recently
    used item, while the tail represents the least recently used item.
    """

    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key: int, value: int):
            self.key = key
            self.value = value
            self.prev = None  # type: LRUCache._Node | None
            self.next = None  # type: LRUCache._Node | None

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache = {}  # key -> node
        # Dummy head and tail nodes to simplify edge cases
        self.head = self._Node(0, 0)
        self.tail = self._Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: "_Node") -> None:
        """Detach a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None and next_node is not None:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: "_Node") -> None:
        """Insert a node right after the head (most recently used)."""
        first_real = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first_real
        if first_real is not None:
            first_real.prev = node

    def get(self, key: int) -> int:
        """Return the value associated with `key` or -1 if it does not exist.
        Marks the key as most recently used."""
        node = self.cache.get(key)
        if node is None:
            return -1
        # Move accessed node to front
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update the value for `key`. Marks it as most recently used.
        Evicts the least recently used item if capacity is exceeded."""
        node = self.cache.get(key)
        if node:
            # Update existing node and move to front
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Insert new node
            new_node = self._Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
            if len(self.cache) > self.capacity:
                # Evict least recently used (node before tail)
                lru = self.tail.prev
                if lru and lru is not self.head:
                    self._remove(lru)
                    del self.cache[lru.key]
