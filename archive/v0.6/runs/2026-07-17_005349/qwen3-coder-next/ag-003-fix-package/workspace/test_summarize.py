#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # (input, expected_output, description)
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}, "empty string"),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}, "only whitespace"),
    ("\n\t\n", {"words": 0, "unique": 0, "avg_len": 0.0}, "only newlines and tabs"),
    (".", {"words": 0, "unique": 0, "avg_len": 0.0}, "only punctuation"),
    ("...", {"words": 0, "unique": 0, "avg_len": 0.0}, "only dots"),
    ("hello", {"words": 1, "unique": 1, "avg_len": 5.0}, "single word"),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}, "two words"),
    ("hello hello", {"words": 2, "unique": 1, "avg_len": 5.0}, "duplicate words"),
    ("Hello HELLO hello", {"words": 3, "unique": 1, "avg_len": 5.0}, "case insensitive"),
    ("Dog.", "dog", {"words": 2, "unique": 1, "avg_len": 3.0}, "punctuation stripping"),
    ("hello\nworld\ttest", {"words": 3, "unique": 3, "avg_len": 5.0}, "different whitespace"),
    ("...hello...", {"words": 1, "unique": 1, "avg_len": 5.0}, "punctuation on both sides"),
    ('"quoted"', {"words": 1, "unique": 1, "avg_len": 6.0}, "quotes around word"),
]

print("Testing summarize function:\n")
for i, (inp, expected, desc) in enumerate(tests, 1):
    try:
        result = summarize(inp)
        passed = result == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status} Test {i}: {desc}")
        if not passed:
            print(f"       Input: {repr(inp)}")
            print(f"       Expected: {expected}")
            print(f"       Got:      {result}")
    except Exception as e:
        print(f"ERROR Test {i}: {desc}")
        print(f"       Exception: {e}")
