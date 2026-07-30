'''Top-level shim to allow ``import toolkit`` when the package directory is not on the import path.
This mirrors the public API defined in ``toolkit/__init__.py``.
'''
import importlib

_pkg = importlib.import_module('toolkit')  # the package directory
# Re‑export the symbols expected by the test suite
days_in_month = _pkg.days_in_month
is_leap_year = _pkg.is_leap_year
mean = _pkg.mean
median = _pkg.median
mode_of = _pkg.mode_of
snake_case = _pkg.snake_case
title_case = _pkg.title_case
truncate = _pkg.truncate

__all__ = [
    "days_in_month",
    "is_leap_year",
    "mean",
    "median",
    "mode_of",
    "snake_case",
    "title_case",
    "truncate",
]
