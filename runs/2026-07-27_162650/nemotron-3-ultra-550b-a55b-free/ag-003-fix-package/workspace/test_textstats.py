import textstats

# Test cases based on spec
tests = [
    # Basic test
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Multiple spaces
    ("Hello    world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Tabs and newlines
    ("Hello\tworld\nfoo", {"words": 3, "unique": 3, "avg_len": 4.33}),
    
    # Case insensitive
    ("Dog dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Punctuation stripping
    ("Dog. dog!", {"words": 2, "unique": 1, "avg_len": 3.0}),
    ("Dog... dog!!", {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Punctuation only tokens (should not count as words)
    ("Hello ... world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Empty input
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Mixed
    ("Hello, world! Hello...", {"words": 3, "unique": 2, "avg_len": 5.0}),
    
    # More punctuation
    ("(Hello) [world]", {"words": 2, "unique": 2, "avg_len": 5.0}),
]

print("Running tests...")
all_pass = True
for i, (text, expected) in enumerate(tests):
    result = textstats.summarize(text)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{status} Test {i+1}: {repr(text)}")
    if result != expected:
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")

if all_pass:
    print("\nAll tests passed!")
else:
    print("\nSome tests failed!")