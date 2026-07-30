import sys
sys.path.insert(0, '.')

from toolkit import (days_in_month, is_leap_year, mean, median, mode_of,
                     snake_case, title_case, truncate)

# Test the 3 failing tests
print("Testing leap century rule...")
assert is_leap_year(2000) is True
assert is_leap_year(1900) is False
assert is_leap_year(2100) is False
assert days_in_month(1900, 2) == 28
print("PASS")

print("Testing median even length...")
assert median([1, 2, 3, 4]) == 2.5
assert median([5, 1]) == 3
assert median([10, 2, 8, 4]) == 6
print("PASS")

print("Testing title case apostrophes...")
assert title_case("it's a dog's life") == "It's A Dog's Life"
assert title_case("o'neill's") == "O'neill's"
print("PASS")

print("All 3 regression tests pass!")