import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
    "HIGHEST_ACCOUNT": "ACCT-16",
    "HIGHEST_BALANCE": 2171,
    "LOWEST_ACCOUNT": "ACCT-25",
    "NET_TOTAL": -9036,
    "NUM_NEGATIVE": 18,
    "NUM_ACTIVE": 197,
}


def _last(label):
    m = re.findall(rf"(?im)^\s*\**\s*{label}\s*\**\s*[:=]\s*(.+?)\s*$", TEXT)
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
    v = v.replace(",", "").replace("\u2212", "-")
    xs = re.findall(r"-?\d+", v)
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


def test_num_active():
    assert _int("NUM_ACTIVE") == EXPECT["NUM_ACTIVE"]
