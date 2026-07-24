"""ctx-013 grader: five independent checkpoints over the settled-balance
aggregation, so retrieving most of the ledger correctly but slipping one derived
value earns partial credit. Reference values are computed by the generator in
tasks-refs/ctx-013-ledger-supersede-64k/generate.py (fixed seed). Only the last
occurrence of each label is read, so mid-reasoning mentions don't fool it.
"""
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
    "HIGHEST_ACCOUNT": "ACCT-14",
    "HIGHEST_BALANCE": 2059,
    "LOWEST_ACCOUNT": "ACCT-03",
    "NET_TOTAL": -15437,
    "NUM_NEGATIVE": 20,
}


def _last(label):
    m = re.findall(rf"(?im)^\s*{label}\s*[:=]\s*(.+?)\s*$", TEXT)
    return m[-1].strip() if m else None


def _acct(label):
    v = _last(label)
    if not v:
        return None
    m = re.search(r"ACCT-\d{2}", v.upper())
    return m.group(0) if m else None


def _int(label):
    v = _last(label)
    if v is None:
        return None
    xs = re.findall(r"-?\d+", v.replace(",", ""))
    return int(xs[0]) if xs else None


def test_highest_account():
    assert _acct("HIGHEST_ACCOUNT") == EXPECT["HIGHEST_ACCOUNT"]


def test_highest_balance():
    assert _int("HIGHEST_BALANCE") == EXPECT["HIGHEST_BALANCE"]


def test_lowest_account():
    assert _acct("LOWEST_ACCOUNT") == EXPECT["LOWEST_ACCOUNT"]


def test_net_total():
    assert _int("NET_TOTAL") == EXPECT["NET_TOTAL"]


def test_num_negative():
    assert _int("NUM_NEGATIVE") == EXPECT["NUM_NEGATIVE"]
