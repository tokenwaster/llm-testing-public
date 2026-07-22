"""Grading suite for the regression hunt.

Three target regressions must be fixed. The twelve load-bearing behaviors
must STAY working — so each target test also asserts every guard is intact
(`_guards_intact()` first). Consequences:
  - untouched seed (3 bugs present)        -> 0/3 = 0.0  (targets fail)
  - all 3 fixed, nothing broken            -> 3/3 = 1.0
  - 2 of 3 fixed, nothing broken           -> 2/3 = 0.667
  - any load-bearing behavior broken       -> 0/3 = 0.0  (guards fail in every
                                              test — "a fix that breaks a
                                              passing test costs what it gains")
A no-op no longer collects the 12 guards as free credit."""
import pytest

from toolkit import (days_in_month, is_leap_year, mean, median, mode_of,
                     snake_case, title_case, truncate)


def _guards_intact():
    """The 12 load-bearing behaviors — must hold before AND after any fix.
    Called at the top of every target test so breaking a guard fails all."""
    assert is_leap_year(2024) is True
    assert is_leap_year(2023) is False
    assert days_in_month(2023, 1) == 31
    assert days_in_month(2024, 2) == 29
    assert days_in_month(2023, 2) == 28
    assert days_in_month(2023, 4) == 30
    with pytest.raises(ValueError):
        days_in_month(2023, 13)
    assert mean([1, 2, 3]) == 2
    assert mean([1.5, 2.5]) == 2.0
    with pytest.raises(ValueError):
        mean([])
    assert median([3, 1, 2]) == 2
    assert median([9, 1, 5, 3, 7]) == 5
    assert median([7]) == 7
    assert mode_of([1, 2, 2, 3]) == 2
    assert mode_of([3, 1, 3, 1]) == 3
    with pytest.raises(ValueError):
        mode_of([])
    assert title_case("hello world") == "Hello World"
    assert title_case("HELLO") == "Hello"
    assert snake_case("CamelCaseString") == "camel_case_string"
    assert snake_case("already_snake") == "already_snake"
    assert snake_case("with space") == "with_space"
    assert truncate("short", 10) == "short"
    assert truncate("abcdefgh", 5) == "abcd…"
    assert len(truncate("abcdefgh", 5)) == 5



def test_fix_leap_century_rule():
    _guards_intact()
    assert is_leap_year(2000) is True
    assert is_leap_year(1900) is False
    assert is_leap_year(2100) is False
    assert days_in_month(1900, 2) == 28


def test_fix_median_even_length():
    _guards_intact()
    assert median([1, 2, 3, 4]) == 2.5
    assert median([5, 1]) == 3
    assert median([10, 2, 8, 4]) == 6


def test_fix_title_case_apostrophes():
    _guards_intact()
    assert title_case("it's a dog's life") == "It's A Dog's Life"
    assert title_case("o'neill's") == "O'neill's"
