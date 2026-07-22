import textstats
import sys

def run_test(input_text, expected):
    """Runs the summarize function and compares results."""
    try:
        result = textstats.summarize(input_text)
        print(f"Input: '{input_text}'")
        print(f"Result: {result}")
        
        # Simple comparison for verification
        if result == expected:
            print("Status: PASS ✅")
        else:
            print(f"Status: FAIL ❌ (Expected: {expected})")

    except Exception as e:
        print(f"Status: ERROR 🛑 ({e})")


# Test Case 1: Basic functionality, punctuation, and case sensitivity.
# Expected avg_len calculation check: Total length = 55. Word count = 17. Avg = 3.24.
run_test("The quick brown fox jumps over the lazy dog. Dog! Is it a day? Yes, it is.", {"words": 17, "unique": 13, "avg_len": 3.24})

# Test Case 2: Whitespace handling (tabs, newlines, multiple spaces).
run_test("Word1\tWord2 \n Word3", {"words": 3, "unique": 3, "avg_len": 5.0})

# Test Case 3: Only punctuation (should count as 0 words).
run_test("... , ; : ! ? \" ' ( )", {"words": 0, "unique": 0, "avg_len": 0.0})

# Test Case 4: Empty input string.
run_test("", {"words": 0, "unique": 0, "avg_len": 0.0})

# Test Case 5: Input with only whitespace.
run_test(" \t\n ", {"words": 0, "unique": 0, "avg_len": 0.0})