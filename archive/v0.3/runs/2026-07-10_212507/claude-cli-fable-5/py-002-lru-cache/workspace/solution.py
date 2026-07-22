class LRUCache:
    """Least-recently-used cache with O(1) get and put.

    Uses a dict for key lookup combined with a doubly linked list
    (with sentinel head/tail nodes) to track usage order. The node
    nearest the head is the least recently used; the node nearest
    the tail is the most recently used.
    """

    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._map = {}
        # Sentinels: head <-> tail; real nodes live between them.
        self._head = self._Node(0, 0)
        self._tail = self._Node(0, 0)
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_tail(self, node):
        node.prev = self._tail.prev
        node.next = self._tail
        self._tail.prev.next = node
        self._tail.prev = node

    def get(self, key: int) -> int:
        node = self._map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._add_to_tail(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add_to_tail(node)
            return
        if len(self._map) >= self.capacity:
            lru = self._head.next
            self._remove(lru)
            del self._map[lru.key]
        node = self._Node(key, value)
        self._map[key] = node
        self._add_to_tail(node)
