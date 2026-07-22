#!/usr/bin/env python3
"""Additional edge case tests for textstats.summarize"""

from textstats import summarize

# Additional edge cases
tests = [
    # Single word with punctuation
    ("Hello!", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Multiple punctuations at edges
    ('"""Hello"""', {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Punctuation in middle should stay (not stripped)
    ("don't stop", {"words": 2, "unique": 2, "avg_len": round((4+4)/2, 2)}),  # "don" and "t" or "don't"? Let's see
    
    # Just whitespace
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    
    # Leading/trailing punctuation only
    (".hello.", {"words": 1, "unique": 1, "avg_len": 5.0}),
    
    # Mixed case with punctuation
    ("Hello, HELLO, hello", {"words": 3, "unique": 1, "avg_len": 5.0}),
]

print("Running edge case tests...")
passed = 0
failed = 0

for i, (text, expected) in enumerate(tests):
    result = summarize(text)
    print("\nTest %d: %r" % (i+1, text))
    print("  Expected: %s" % expected)
    print("  Got:      %s" % result)
    
    try:
        if (result["words"] == expected["words"] and 
            result["unique"] == expected["unique"] and 
            abs(result.get("avg_len", 0) - expected["avg_len"]) <= 0.01):
            print("  PASS")
            passed += 1
        else:
            print("  FAIL")
            failed += 1
    except Exception as e:
        print("  ERROR: %s" % e)
        failed += 1

print("\n" + "="*50)
print("Results: %d passed, %d failed" % (passed, failed))
