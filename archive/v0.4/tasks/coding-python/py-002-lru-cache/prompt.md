Implement a class `LRUCache` (least-recently-used cache):

- `LRUCache(capacity: int)` — fixed positive capacity.
- `get(key) -> value` — return the stored value, or `-1` if absent. A successful
  `get` marks the key as most recently used.
- `put(key, value) -> None` — insert or update. Updating an existing key marks it
  most recently used. When inserting a **new** key at capacity, evict the least
  recently used key first.

Both operations must run in O(1) average time. Keys and values are integers.
