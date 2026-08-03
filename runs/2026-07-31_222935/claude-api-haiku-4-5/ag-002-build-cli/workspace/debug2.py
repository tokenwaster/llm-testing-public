from collections import Counter

word_counter = Counter({'test': 3, 'hello': 2, 'world': 1})
print("Items:", list(word_counter.items()))

# Test the key function
items = list(word_counter.items())
for item in items:
    key = (-item[1], item[0])
    print(f"{item} -> {key}")

result = max(word_counter.items(), key=lambda x: (-x[1], x[0]))
print(f"Max result: {result}")

# Alternative approach
sorted_items = sorted(word_counter.items(), key=lambda x: (-x[1], x[0]))
print(f"Sorted: {sorted_items}")
print(f"First: {sorted_items[0]}")
