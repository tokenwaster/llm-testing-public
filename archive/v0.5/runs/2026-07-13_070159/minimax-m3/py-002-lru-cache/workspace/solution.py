class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """Least-recently-used cache with O(1) average-time get and put."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}

        # Sentinel head/tail make list operations branch-free.
        # head <-> ... <-> tail
        # MRU is just after `head`; LRU is just before `tail`.
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: _Node) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        node = self.cache.get(key)
        if node is None:
            return -1
        # Mark as most recently used.
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.cache.get(key)
        if node is not None:
            # Update existing entry; mark as most recently used.
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return

        # Inserting a new key.
        if len(self.cache) >= self.capacity:
            # Evict the least recently used entry (node just before tail).
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]

        new_node = _Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node
