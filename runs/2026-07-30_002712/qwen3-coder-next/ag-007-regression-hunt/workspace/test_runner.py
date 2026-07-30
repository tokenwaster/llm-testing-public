import sys
sys.path.insert(0, '.')

from toolkit import (days_in_month, is_leap_year, mean, median, mode_of,
                     snake_case, title_case, truncate)
import traceback

print("=== Testing is_leap_year ===")
try:
    result = is_leap_year(2000)
    print(f"is_leap_year(2000) = {result}, expected True - {'PASS' if result == True else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

try:
    result = is_leap_year(1900)
    print(f"is_leap_year(1900) = {result}, expected False - {'PASS' if result == False else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

print("\n=== Testing median ===")
try:
    result = median([3, 1, 2])
    print(f"median([3, 1, 2]) = {result}, expected 2 - {'PASS' if result == 2 else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

try:
    result = median([9, 1, 5, 3, 7])
    print(f"median([9, 1, 5, 3, 7]) = {result}, expected 5 - {'PASS' if result == 5 else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

try:
    result = median([1, 2, 3, 4])
    print(f"median([1, 2, 3, 4]) = {result}, expected 2.5 - {'PASS' if result == 2.5 else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

print("\n=== Testing title_case ===")
try:
    result = title_case("it's a dog's life")
    expected = "It's A Dog's Life"
    print(f"title_case(\"it's a dog's life\") = \"{result}\", expected \"{expected}\" - {'PASS' if result == expected else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

try:
    result = title_case("o'neill's")
    expected = "O'neill's"
    print(f"title_case(\"o'neill's\") = \"{result}\", expected \"{expected}\" - {'PASS' if result == expected else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

print("\n=== Testing truncate ===")
try:
    result = truncate("abcdefgh", 5)
    expected = "abcd…"
    print(f"truncate(\"abcdefgh\", 5) = \"{result}\", expected \"{expected}\" - {'PASS' if result == expected else 'FAIL'}")
except Exception as e:
    traceback.print_exc()

try:
    result = truncate("abcdefgh", 5)
    length_result = len(result)
    print(f"len(truncate(\"abcdefgh\", 5)) = {length_result}, expected 5 - {'PASS' if length_result == 5 else 'FAIL'}")
except Exception as e:
    traceback.print_exc()
