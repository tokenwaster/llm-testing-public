from collections import OrderedDict
from typing import Dict

class LRUCache:
    """
    Least-Recently-Used (LRU) cache with O(1) average time for get and put.

    Attributes
    ----------
    capacity : int
        Maximum number of key/value pairs the cache can hold.
    _cache : OrderedDict[int, int]
        Stores the items; order reflects recency (most recent at the end).
    """

    def __init__(self, capacity: int):
        """
        Initialize the cache with a fixed positive capacity.

        Parameters
        ----------
        capacity : int
            The maximum number of entries the cache can contain.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity: int = capacity
        self._cache: "OrderedDict[int, int]" = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with `key` and mark it as most recently used.

        Parameters
        ----------
        key : int
            The key to look up.

        Returns
        -------
        int
            The stored value, or -1 if the key is not present.
        """
        if key not in self._cache:
            return -1
        # Move the accessed key to the end to denote recent use
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Insert a new key/value pair or update an existing one.
        Marks the key as most recently used. If insertion would exceed capacity,
        evicts the least recently used key first.

        Parameters
        ----------
        key : int
            The key to insert or update.
        value : int
            The value to associate with `key`.
        """
        if key in self._cache:
            # Update existing entry and move it to the end
            self._cache[key] = value
            self._cache.move_to_end(key)
        else:
            # Insert new entry
            if len(self._cache) >= self.capacity:
                # Evict least-recently-used (first) item
                self._cache.popitem(last=False)
            self._cache[key] = value
