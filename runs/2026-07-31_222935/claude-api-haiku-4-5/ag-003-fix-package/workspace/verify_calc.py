from textstats import summarize

# Test with clear calculation
print("Test: 'Hello world'")
print("  'Hello' length: 5")
print("  'world' length: 5")
print("  Average: (5 + 5) / 2 = 5.0")
result = summarize("Hello world")
print(f"  Result: {result}")
print()

# Test with uneven average
print("Test: 'Hi world'")
print("  'Hi' length: 2")
print("  'world' length: 5")
print("  Average: (2 + 5) / 2 = 3.5")
result = summarize("Hi world")
print(f"  Result: {result}")
print()

# Test with three words
print("Test: 'Hello world test'")
print("  'Hello' length: 5")
print("  'world' length: 5")
print("  'test' length: 4")
print("  Average: (5 + 5 + 4) / 3 = 4.67")
result = summarize("Hello world test")
print(f"  Result: {result}")
