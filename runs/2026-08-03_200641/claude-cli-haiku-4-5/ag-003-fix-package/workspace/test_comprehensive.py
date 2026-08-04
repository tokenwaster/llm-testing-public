#!/usr/bin/env python3
"""Comprehensive tests for textstats.summarize()"""

from textstats import summarize

def test_case(name, text, expected):
    result = summarize(text)
    passed = result == expected
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if not passed:
        print(f"  Got:      {result}")
        print(f"  Expected: {expected}")
    return passed

all_passed = True

# Empty and punctuation-only cases
all_passed &= test_case(
    "Empty string",
    "",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)

all_passed &= test_case(
    "Only punctuation",
    ".,;:!?\"'()",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)

all_passed &= test_case(
    "Punctuation with spaces",
    ". , ; : ! ? \" ' ( )",
    {"words": 0, "unique": 0, "avg_len": 0.0}
)

# Case insensitivity
all_passed &= test_case(
    "Case insensitivity",
    "Dog dog DOG",
    {"words": 3, "unique": 1, "avg_len": 3.0}
)

all_passed &= test_case(
    "Mixed case with punctuation",
    "Dog. dog DOG's",
    {"words": 3, "unique": 2, "avg_len": 3.67}
)

# Whitespace handling
all_passed &= test_case(
    "Multiple spaces",
    "hello    world",
    {"words": 2, "unique": 2, "avg_len": 5.0}
)

all_passed &= test_case(
    "Tabs and newlines",
    "hello\tworld\nfoo  bar",
    {"words": 4, "unique": 4, "avg_len": 4.0}
)

# Mixed punctuation and case
all_passed &= test_case(
    "Mixed punctuation",
    "Hello, world! How's (it) going?",
    {"words": 5, "unique": 5, "avg_len": 4.4}
)

# Average length rounding
all_passed &= test_case(
    "Avg length with rounding",
    "a bb ccc",  # lengths: 1, 2, 3 → sum=6, avg=2.0
    {"words": 3, "unique": 3, "avg_len": 2.0}
)

all_passed &= test_case(
    "Avg length with decimals",
    "ab abc abcd",  # lengths: 2, 3, 4 → sum=9, avg=3.0
    {"words": 3, "unique": 3, "avg_len": 3.0}
)

# Real-world example
all_passed &= test_case(
    "Real example with various punctuation",
    "The quick, brown fox jumps over the lazy dog.",
    {"words": 9, "unique": 8, "avg_len": 3.89}
)

print()
print("=" * 50)
if all_passed:
    print("All tests PASSED!")
else:
    print("Some tests FAILED!")
