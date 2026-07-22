class LRUCache:
    """Least-recently-used cache with O(1) get and put.

    Implemented as a hash map plus a doubly linked list with sentinel
    head/tail nodes. Nodes near the head are most recently used; the
    node just before the tail is the eviction candidate.
    """

    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key: int, value: int) -> None:
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._map = {}
        self._head = self._Node(0, 0)  # sentinel: most recent side
        self._tail = self._Node(0, 0)  # sentinel: least recent side
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: "_Node") -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: "_Node") -> None:
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: int) -> int:
        node = self._map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return
        if len(self._map) >= self.capacity:
            lru = self._tail.prev
            self._remove(lru)
            del self._map[lru.key]
        node = self._Node(key, value)
        self._map[key] = node
        self._add_to_front(node)
