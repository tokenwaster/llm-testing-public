class LRUCache:
    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._map = {}
        # Sentinel head/tail: head.next is most recently used,
        # tail.prev is least recently used.
        self._head = self._Node(None, None)
        self._tail = self._Node(None, None)
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node):
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: int) -> int:
        node = self._map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._add_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add_front(node)
            return
        if len(self._map) >= self.capacity:
            lru = self._tail.prev
            self._remove(lru)
            del self._map[lru.key]
        node = self._Node(key, value)
        self._map[key] = node
        self._add_front(node)
