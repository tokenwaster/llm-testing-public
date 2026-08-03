from collections import Counter

word_counter = Counter({'test': 3, 'hello': 2, 'world': 1})

# The key function returns tuples like (-3, 'test')
# max should compare these tuples lexicographically
# (-3, 'test') < (-2, 'hello') < (-1, 'world')
# So max should return (-1, 'world')

# Let me verify tuple comparison
print((-3, 'test') < (-2, 'hello'))  # True
print((-2, 'hello') < (-1, 'world'))  # True
print(max([(-3, 'test'), (-2, 'hello'), (-1, 'world')]))  # Should be (-1, 'world')

# So max is working correctly with the key function, but returning the wrong thing
# Let me check what max actually does
result = max(word_counter.items(), key=lambda x: (-x[1], x[0]))
print(f"Result: {result}")

# The issue is that max() returns the original item, not the key!
# So it's returning the item whose key is the largest
# (-1, 'world') > (-2, 'hello') > (-3, 'test')
# So max returns the item with key (-1, 'world') which is ('world', 1)

# This is wrong! We want the item with the SMALLEST negative count (largest positive count)
# So we need (-3, 'test') which is the minimum key

result = min(word_counter.items(), key=lambda x: (-x[1], x[0]))
print(f"Min result: {result}")
