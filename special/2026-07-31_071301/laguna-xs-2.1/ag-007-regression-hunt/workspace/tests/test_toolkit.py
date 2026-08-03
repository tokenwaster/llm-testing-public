import pytest

from toolkit import (days_in_month, is_leap_year, mean, median, mode_of,
                     snake_case, title_case, truncate)



def test_leap_century_rule():
    assert is_leap_year(2000) is True
    assert is_leap_year(1900) is False
    assert is_leap_year(2100) is False
    assert days_in_month(1900, 2) == 28


def test_median_even_length():
    assert median([1, 2, 3, 4]) == 2.5
    assert median([5, 1]) == 3
    assert median([10, 2, 8, 4]) == 6


def test_title_case_apostrophes():
    assert title_case("it's a dog's life") == "It's A Dog's Life"
    assert title_case("o'neill's") == "O'neill's"



def test_leap_simple():
    assert is_leap_year(2024) is True
    assert is_leap_year(2023) is False


def test_days_in_month_basic():
    assert days_in_month(2023, 1) == 31
    assert days_in_month(2024, 2) == 29
    assert days_in_month(2023, 2) == 28
    assert days_in_month(2023, 4) == 30


def test_days_bad_month():
    with pytest.raises(ValueError):
        days_in_month(2023, 13)


def test_mean():
    assert mean([1, 2, 3]) == 2
    assert mean([1.5, 2.5]) == 2.0
    with pytest.raises(ValueError):
        mean([])


def test_median_odd_length():
    assert median([3, 1, 2]) == 2
    assert median([9, 1, 5, 3, 7]) == 5


def test_median_single():
    assert median([7]) == 7


def test_mode_basic():
    assert mode_of([1, 2, 2, 3]) == 2


def test_mode_tie_first_appearance():
    assert mode_of([3, 1, 3, 1]) == 3


def test_mode_empty_raises():
    with pytest.raises(ValueError):
        mode_of([])


def test_title_basic():
    assert title_case("hello world") == "Hello World"
    assert title_case("HELLO") == "Hello"


def test_snake_case():
    assert snake_case("CamelCaseString") == "camel_case_string"
    assert snake_case("already_snake") == "already_snake"
    assert snake_case("with space") == "with_space"


def test_truncate():
    assert truncate("short", 10) == "short"
    assert truncate("abcdefgh", 5) == "abcd…"
    assert len(truncate("abcdefgh", 5)) == 5
