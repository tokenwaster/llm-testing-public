#!/usr/bin/env python3
"""Comprehensive test for textstats.summarize"""

from textstats import summarize

# Test cases: (input, expected_output, description)
tests = [
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}, "empty string"),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}, "only whitespace"),
    ("\n\t\n", {"words": 0, "unique": 0, "avg_len": 0.0}, "only newlines and tabs"),
    (".", {"words": 0, "unique": 0, "avg_len": 0.0}, "only punctuation"),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}, "only dots"),
    ("hello", {"words": 1, "unique": 1, "avg_len": 5.0}, "single word"),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}, "two words"),
    ("hello hello", {"words": 2, "unique": 1, "avg_len": 5.0}, "duplicate words"),
    ("Hello HELLO hello", {"words": 3, "unique": 1, "avg_len": 5.0}, "case insensitive"),
    ("Dog.", {"words": 1, "unique": 1, "avg_len": 3.0}, "trailing punctuation"),
    (".dog", {"words": 1, "unique": 1, "avg_len": 3.0}, "leading punctuation"),
    ("(dog)", {"words": 1, "unique": 1, "avg_len": 3.0}, "punctuation on both sides"),
    ("hello\nworld\ttest", {"words": 3, "unique": 3, "avg_len": 5.0}, "different whitespace"),
    ("...hello...", {"words": 1, "unique": 1, "avg_len": 5.0}, "punctuation on both sides"),
    ('"quoted"', {"words": 1, "unique": 1, "avg_len": 6.0}, "quotes around word"),
    ("Hello, world!", {"words": 2, "unique": 2, "avg_len": 5.5}, "punctuation mixed with words"),
    ("   hello   world   ", {"words": 2, "unique": 2, "avg_len": 5.0}, "extra spaces"),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}, "empty string again"),
]

print("Comprehensive testing of summarize function:\n")
passed = 0
failed = 0

for i, (inp, expected, desc) in enumerate(tests, 1):
    try:
        result = summarize(inp)
        if result == expected:
            print(f"PASS Test {i}: {desc}")
            passed += 1
        else:
            print(f"FAIL Test {i}: {desc}")
            print(f"       Input: {repr(inp)}")
            print(f"       Expected: {expected}")
            print(f"       Got:      {result}")
            failed += 1
    except Exception as e:
        print(f"ERROR Test {i}: {desc}")
        print(f"       Exception: {e}")
        failed += 1

print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
