#!/usr/bin/env python3
"""Simple test for textstats.summarize"""

from textstats import summarize

# Test empty string
print("Test 1: empty string")
try:
    result = summarize("")
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")

# Test only whitespace
print("\nTest 2: only whitespace")
try:
    result = summarize("   ")
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")

# Test different whitespace
print("\nTest 3: different whitespace")
try:
    result = summarize("\n\t\n")
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")

# Test case insensitive
print("\nTest 4: case insensitive")
try:
    result = summarize("Hello HELLO hello")
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")
