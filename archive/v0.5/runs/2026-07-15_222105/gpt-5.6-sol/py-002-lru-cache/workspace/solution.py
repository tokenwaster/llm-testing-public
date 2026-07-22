class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}

        self.head = _Node()  # Least recently used side
        self.tail = _Node()  # Most recently used side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_most_recent(self, node: _Node) -> None:
        previous = self.tail.prev
        previous.next = node
        node.prev = previous
        node.next = self.tail
        self.tail.prev = node

    def get(self, key: int) -> int:
        node = self.cache.get(key)
        if node is None:
            return -1

        self._remove(node)
        self._append_most_recent(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.cache.get(key)

        if node is not None:
            node.value = value
            self._remove(node)
            self._append_most_recent(node)
            return

        if len(self.cache) >= self.capacity:
            least_recent = self.head.next
            self._remove(least_recent)
            del self.cache[least_recent.key]

        node = _Node(key, value)
        self.cache[key] = node
        self._append_most_recent(node)
