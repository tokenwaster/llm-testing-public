class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        self.cache = {}

        self.head = _Node()  # Least recently used side
        self.tail = _Node()  # Most recently used side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_end(self, node: _Node) -> None:
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        node = self.cache.get(key)
        if node is None:
            return -1

        self._remove(node)
        self._insert_at_end(node)
        return node.value

    def put(self, key, value) -> None:
        node = self.cache.get(key)

        if node is not None:
            node.value = value
            self._remove(node)
            self._insert_at_end(node)
            return

        node = _Node(key, value)
        self.cache[key] = node
        self._insert_at_end(node)

        if len(self.cache) > self.capacity:
            least_recently_used = self.head.next
            self._remove(least_recently_used)
            del self.cache[least_recently_used.key]
