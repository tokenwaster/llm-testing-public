#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Multiple spaces/tabs/newlines
    ("hello  world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("hello\n\nworld", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("hello\t\t\tworld", {"words": 2, "unique": 2, "avg_len": 5.0}),
    
    # Mixed whitespace
    ("hello \t world\nfoo  bar", {"words": 4, "unique": 4, "avg_len": 4.75}),
    
    # Punctuation handling at start and end
    ('"hello"', {"words": 1, "unique": 1, "avg_len": 5.0}),
    ("'world'", {"words": 1, "unique": 1, "avg_len": 5.0}),
    ("(foo)", {"words": 1, "unique": 1, "avg_len": 3.0}),
    
    # Mixed case with punctuation
    ('"Dog." dog', {"words": 2, "unique": 1, "avg_len": 3.0}),
    
    # Single character words
    ("a b c", {"words": 3, "unique": 3, "avg_len": 1.0}),
    
    # Only whitespace variations
    ("\n\n\n", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("\t\t\t", {"words": 0, "unique": 0, "avg_len": 0.0}),
]

print("Testing edge cases:")
all_passed = True
for i, (inp, expected) in enumerate(tests):
    try:
        result = summarize(inp)
        passed = result == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status} Test {i+1}: input={repr(inp)}")
        if not passed:
            all_passed = False
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
    except Exception as e:
        all_passed = False
        print(f"FAIL Test {i+1}: raised {type(e).__name__}: {e}")

if all_passed:
    print("\nAll edge case tests passed!")
else:
    print("\nSome tests failed!")
