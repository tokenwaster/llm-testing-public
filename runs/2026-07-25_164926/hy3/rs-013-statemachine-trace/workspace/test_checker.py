"""rs-013 grader: five independent checkpoints over the traced final state, so a
model that slips on one op earns partial credit rather than zero. The reference
values are computed by simulating the program in prompt.md under its stated rules
(top->bottom final stack 10,162,6). Only the last occurrence of each label is
read, so scratch work that mentions a label mid-reasoning does not fool it.
"""
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
    "FINAL_STACK": [10, 162, 6],
    "MAX_TOP": 169,
    "REG_R": 5,
    "ODD_POPS": 3,
    "SUM_FINAL": 178,
}


def _last(label: str) -> str | None:
    m = re.findall(rf"(?im)^\s*{label}\s*[:=]\s*(.+?)\s*$", TEXT)
    return m[-1].strip() if m else None


def _ints(s: str) -> list[int]:
    return [int(x) for x in re.findall(r"-?\d+", s)]


def _one_int(label: str):
    v = _last(label)
    if v is None:
        return None
    xs = _ints(v)
    return xs[0] if xs else None


def test_final_stack():
    v = _last("FINAL_STACK")
    assert v is not None and _ints(v) == EXPECT["FINAL_STACK"]


def test_max_top():
    assert _one_int("MAX_TOP") == EXPECT["MAX_TOP"]


def test_reg_r():
    assert _one_int("REG_R") == EXPECT["REG_R"]


def test_odd_pops():
    assert _one_int("ODD_POPS") == EXPECT["ODD_POPS"]


def test_sum_final():
    assert _one_int("SUM_FINAL") == EXPECT["SUM_FINAL"]
