#!/usr/bin/env python3
"""Test script for textstats.summarize"""

from textstats import summarize

# Test cases
tests = [
    # (input, expected_output_description)
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("hello", {"words": 1, "unique": 1, "avg_len": 5.0}),
    ("hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),  # Dog and dog are same
    ("hello\tworld\nfoo", {"words": 3, "unique": 3, "avg_len": 4.33}),  # tabs/newlines
    (",;:!", {"words": 0, "unique": 0, "avg_len": 0.0}),  # only punctuation
    ("hello... world!!!", {"words": 2, "unique": 2, "avg_len": 5.0}),
]

print("Testing summarize function:")
for i, (inp, expected) in enumerate(tests):
    try:
        result = summarize(inp)
        passed = result == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status} Test {i+1}: input={repr(inp)}")
        if not passed:
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
    except Exception as e:
        print(f"FAIL Test {i+1}: raised {type(e).__name__}: {e}")
