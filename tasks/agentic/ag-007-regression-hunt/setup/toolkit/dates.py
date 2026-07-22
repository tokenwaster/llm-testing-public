_DAYS = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
         7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def is_leap_year(year: int) -> bool:
    """Gregorian leap year rule."""
    return year % 4 == 0


def days_in_month(year: int, month: int) -> int:
    if month not in _DAYS:
        raise ValueError(f"bad month {month}")
    if month == 2 and is_leap_year(year):
        return 29
    return _DAYS[month]
