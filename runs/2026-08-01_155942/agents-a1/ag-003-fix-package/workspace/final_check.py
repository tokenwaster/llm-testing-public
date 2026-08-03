#!/usr/bin/env python3
import sys
from textstats import summarize

# All spec-based tests with correct expected values

tests_passed = 0
total_tests = 0

def run_test(name, fn, expected=None):
    global tests_passed, total_tests
    total_tests += 1
    try:
        result = fn()
        if expected is not None and result != expected:
            print(f"{name}: FAIL - got {result}, expected {expected}")
            return False
        print(f"{name}: PASS")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"{name}: ERROR - {e}")
        return False

# Test 1: basic with mixed punctuation, case insensitivity
run_test("basic", lambda: summarize("Hello, World! This is a test."), {"words":6, "unique":6, "avg_len":3.5})

# Test 2: only punctuation (stripped to empty) - should not raise and return zeros
run_test("only_punctuation", lambda: summarize("! ? ..."), {"words":0, "unique":0, "avg_len":0.0})

# Test 3: empty string returns zeros without error
run_test("empty_string", lambda: summarize(""), {"words":0, "unique":0, "avg_len":0.0})

# Test 4: case insensitivity for unique count (Dog/dog same)
run_test("case_insensitive", lambda: summarize("Dog DOG dog"), {"words":3, "unique":1, "avg_len":3.0})

# Test 5: any whitespace separators (tabs, newlines, multiple spaces)
run_test("whitespace_separators", lambda: summarize("Hello\tworld\nThis   is\tdown"), {"words":5, "unique":5, "avg_len":4.0})

# Test 6: leading/trailing punctuation stripped but internal chars count as word if not in PUNCT set
run_test("hyphen_word", lambda: summarize("'Hello' - world"), {"words":3, "unique":3, "avg_len":3.67})

# Test 7: token that is only from defined punctuation list should be excluded entirely (becomes empty)
run_test("punctuation_only_excluded", lambda: summarize("a . b , c ! d"), {"words":4, "unique":4, "avg_len":1.0})

# Test 8: parentheses around word stripped -> valid token remains
run_test("parentheses_stripped", lambda: summarize("(abc) def (ghi)!"), {"words":3, "unique":3, "avg_len":3.0})

# Test 9: avg_len rounding to 2 decimals for non-integer values; exact case
run_test("rounding_exact", lambda: summarize("ab cd"), {"words":2, "unique":2, "avg_len":2.0})

# Test 10: single word with punctuation becomes clean word
run_test("single_word_punct", lambda: summarize("(Hello),"), {"words":1, "unique":1, "avg_len":5.0})

print(f"\n=== Tests passed: {tests_passed}/{total_tests} ===")
sys.exit(0 if tests_passed == total_tests else 1)
