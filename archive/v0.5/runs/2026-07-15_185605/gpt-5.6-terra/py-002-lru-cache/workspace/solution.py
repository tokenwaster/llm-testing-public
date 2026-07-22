class LRUCache:
    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key=0, value=0):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}

        self.head = self._Node()  # Most recently used side
        self.tail = self._Node()  # Least recently used side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node):
        self._remove(node)
        self._add_to_front(node)

    def get(self, key: int) -> int:
        node = self.cache.get(key)
        if node is None:
            return -1

        self._move_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.cache.get(key)

        if node is not None:
            node.value = value
            self._move_to_front(node)
            return

        if len(self.cache) == self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]

        new_node = self._Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
