import math
import re
from pathlib import Path

import pytest

from solution import evaluate

FORBIDDEN = re.compile(r"\b(eval|exec)\s*\(|import\s+ast|from\s+ast\b|\b__import__\b|\bimportlib\b")


def test_no_eval_or_ast():
    src = (Path(__file__).parent / "solution.py").read_text(encoding="utf-8")
    assert not FORBIDDEN.search(src), "solution must not use eval/exec/ast"


def test_basic_precedence():
    assert evaluate("2+3*4") == 14.0
    assert evaluate("2*3+4") == 10.0
    assert evaluate("10-4-3") == 3.0
    assert evaluate("100/10/5") == 2.0


def test_parentheses():
    assert evaluate("(2+3)*4") == 20.0
    assert evaluate("((1+2)*(3+4))") == 21.0


def test_power_right_assoc():
    assert evaluate("2^3^2") == 512.0
    assert evaluate("(2^3)^2") == 64.0


def test_unary_minus():
    assert evaluate("-3+5") == 2.0
    assert evaluate("--3") == 3.0
    assert evaluate("-2^2") == -4.0
    assert evaluate("2^-1") == 0.5


def test_modulo_and_decimals():
    assert evaluate("7%3") == 1.0
    assert math.isclose(evaluate("1.5*2.5"), 3.75)


def test_variables():
    assert evaluate("x*y+1", {"x": 3, "y": 4}) == 13.0
    assert evaluate("long_name2 - 1", {"long_name2": 2.5}) == 1.5


def test_whitespace():
    assert evaluate("  2 +   3\t* 4 ") == 14.0


def test_errors():
    for bad in ["2+", "(2+3", "2 3", "2*/3", "", ")2(", "1+*2"]:
        with pytest.raises(ValueError):
            evaluate(bad)
    with pytest.raises(ValueError):
        evaluate("nope+1")
    with pytest.raises(ValueError):
        evaluate("1/0")
    with pytest.raises(ValueError):
        evaluate("5%0")
