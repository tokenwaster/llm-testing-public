#!/usr/bin/env python3
"""Comprehensive test suite for textstats.summarize()."""

from textstats import summarize

def test(description, text, expected):
    """Test helper."""
    try:
        result = summarize(text)
        match = result == expected
        status = "PASS" if match else "FAIL"
        print(f"[{status}] {description}")
        if not match:
            print(f"    Got:      {result}")
            print(f"    Expected: {expected}")
    except Exception as e:
        print(f"[FAIL] {description}")
        print(f"    ERROR: {type(e).__name__}: {e}")
        print(f"    Expected: {expected}")

# Whitespace handling
test(
    "Multiple spaces",
    "hello  world",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)
test(
    "Tabs and newlines",
    "hello\t\nworld  test",
    {"words": 3, "unique": 3, "avg_len": 4.67}
)
test(
    "Leading/trailing whitespace",
    "  hello world  ",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)

# Case-insensitivity
test(
    "Same word different cases",
    "Dog dog DOG",
    {"words": 3, "unique": 1, "avg_len": 3.0}
)
test(
    "Mixed cases",
    "Hello HELLO hello HeLLo",
    {"words": 4, "unique": 1, "avg_len": 5.0}
)

# Punctuation stripping
test(
    "Punctuation at ends",
    "Hello, world!",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)
test(
    "Quotes and parens",
    "\"quoted\" (word)",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)
test(
    "Mixed punctuation",
    "Hello, world! How's \"it\"?",
    {"words": 4, "unique": 4, "avg_len": 4.25}
)

# Empty/no-words cases
test(
    "Empty string",
    "",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)
test(
    "Only whitespace",
    "   \t\n  ",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)
test(
    "Only punctuation",
    ".,;:!?\"'()",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)
test(
    "Punctuation with whitespace",
    ", . ; :",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)

# Edge cases
test(
    "Single word",
    "hello",
    {"words": 1, "unique": 1, "avg_len": 5.0}
)
test(
    "Single character",
    "a",
    {"words": 1, "unique": 1, "avg_len": 1.0}
)
test(
    "Apostrophe in middle (not stripped)",
    "don't can't",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)

print("\nAll tests completed!")
