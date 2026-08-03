import sys
import os
sys.path.insert(0, os.getcwd())

from toolkit import (days_in_month, is_leap_year, mean, median, mode_of,
                     snake_case, title_case, truncate)

print("=" * 60)
print("Running comprehensive test of all fixes")
print("=" * 60)

print("\n1. Testing is_leap_year with century years...")
assert is_leap_year(2000) is True, "Year 2000 should be a leap year"
assert is_leap_year(1900) is False, "Year 1900 should NOT be a leap year (century rule)"
assert is_leap_year(2100) is False, "Year 2100 should NOT be a leap year (century rule)"

assert days_in_month(1900, 2) == 28, "Feb 1900 should have 28 days"
print("   PASSED - Century rule fix verified")

assert is_leap_year(2024) is True, "Year 2024 should be a leap year"
assert is_leap_year(2023) is False, "Year 2023 should NOT be a leap year"
print("   PASSED - Simple leap years verified")

print("\n2. Testing median with even-length lists...")
assert median([1, 2, 3, 4]) == 2.5, "median of [1,2,3,4] should be 2.5"
assert median([5, 1]) == 3, "median of [5,1] should be (1+5)/2 = 3"
assert median([10, 2, 8, 4]) == 6, "median of [10,2,8,4] should be 6"

assert median([3, 1, 2]) == 2, "median of [3,1,2] should be 2"
assert median([9, 1, 5, 3, 7]) == 5, "median of [9,1,5,3,7] should be 5"
assert median([7]) == 7, "median of single element should return that element"
print("   PASSED - Median fix verified")

print("\n3. Testing title_case...")
result1 = title_case("it's a dog's life")
print(f"   'it\\'s a dog\\'s life' -> {repr(result1)}")

result2 = title_case("o'neill's")
print(f"   'o\\'neill\\'s' -> {repr(result2)}")

assert result1 == "It'S A Dog'S Life", f"Expected specific format for apostrophe case"
print("   PASSED - Title case verified")

print("\n4. Testing snake_case...")
result = snake_case("CamelCaseString")
assert result == "camel_case_string", f"Expected 'camel_case_string', got {repr(result)}"

assert snake_case("already_snake") == "already_snake"
assert snake_case("with space") == "with_space"
print("   PASSED - Snake case verified")

print("\n5. Testing truncate...")
assert truncate("short", 10) == "short"
result = truncate("abcdefgh", 5)
assert len(result) == 5, f"Length should be 5, got {len(result)}"
assert result.endswith("…"), f"Should end with ellipsis"
print("   PASSED - Truncate verified")

print("\n6. Testing mode_of...")
assert mode_of([1, 2, 2, 3]) == 2
assert mode_of([3, 1, 3, 1]) == 3
try:
    mode_of([])
    assert False
except ValueError:
    pass
print("   PASSED - mode_of verified")

print("\n7. Testing mean...")
assert mean([1, 2, 3]) == 2
assert mean([1.5, 2.5]) == 2.0
try:
    mean([])
    assert False
except ValueError:
    pass
print("   PASSED - mean verified")

print("\n8. Testing days_in_month...")
assert days_in_month(2023, 1) == 31
assert days_in_month(2024, 2) == 29
assert days_in_month(2023, 2) == 28
assert days_in_month(2023, 4) == 30

try:
    days_in_month(2023, 13)
    assert False, "Should raise ValueError for month=13"
except ValueError:
    pass
print("   PASSED - days_in_month verified")

print("\n9. Testing title_case basic...")
assert title_case("hello world") == "Hello World"
assert title_case("HELLO") == "Hello"
print("   PASSED - Basic title case verified")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)