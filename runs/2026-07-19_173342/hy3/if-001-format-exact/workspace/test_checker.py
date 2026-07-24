"""Constraint checks for if-001: the model's raw reply is response.txt.

Each rule from the prompt is one test, so the score is the fraction of the
format contract the model actually honored. A do-nothing / prose reply fails
every check.
"""
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""
LINES = TEXT.strip().splitlines()
FMT = re.compile(r"^(\S+) - (\d{4})$")


def test_exactly_five_nonblank_lines():
    assert len(LINES) == 5, f"expected 5 lines, got {len(LINES)}"
    assert all(ln.strip() for ln in LINES), "no blank lines allowed"


def test_every_line_matches_name_dash_year():
    assert LINES, "no output"
    bad = [ln for ln in LINES[:5] if not FMT.match(ln)]
    assert not bad, f"lines not in 'NAME - YEAR' form: {bad}"


def test_years_ascending():
    years = [int(m.group(2)) for ln in LINES[:5] if (m := FMT.match(ln))]
    assert len(years) == 5, "could not read five years"
    assert years == sorted(years), f"years not ascending: {years}"


def test_no_python():
    names = [m.group(1).lower() for ln in LINES[:5] if (m := FMT.match(ln))]
    assert len(names) == 5, "need five well-formed 'NAME - YEAR' lines"
    assert "python" not in names, "Python was excluded by the rules"
