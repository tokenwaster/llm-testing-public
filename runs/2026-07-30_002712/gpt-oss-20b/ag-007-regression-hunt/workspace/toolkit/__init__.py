# Toolkit package initialization
# Import submodules and expose selected functions
from . import dates as _dates
from . import stats as _stats
from . import text as _text

# Re-export public API
is_leap_year = _dates.is_leap_year
days_in_month = _dates.days_in_month
mean = _stats.mean
median = _stats.median
mode_of = _stats.mode_of
title_case = _text.title_case
snake_case = _text.snake_case
truncate = _text.truncate

__all__ = [
    "is_leap_year",
    "days_in_month",
    "mean",
    "median",
    "mode_of",
    "title_case",
    "snake_case",
    "truncate",
]
