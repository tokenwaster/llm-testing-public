import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
    "NUM_NODES": 15,
    "NUM_EDGES": 30,
    "REACHABLE": 9,
    "SHORTEST": 3,
    "MAX_OUT_NODE": "EMBER",
    "MAX_OUT_DEGREE": 4,
    "HAS_CYCLE": "YES",
}


def _last(label):
    m = re.findall(rf"(?im)^\s*\**\s*{label}\s*\**\s*[:=]\s*(.+?)\s*$", TEXT)
    return m[-1].strip() if m else None


def _int(label):
    v = _last(label)
    if v is None:
        return None
    xs = re.findall(r"-?\d+", v.replace(",", ""))
    return int(xs[0]) if xs else None


def _word(label):
    v = _last(label)
    if not v:
        return None
    m = re.search(r"[A-Z]{3,}", v.upper())
    return m.group(0) if m else None


def test_num_nodes():
    assert _int("NUM_NODES") == EXPECT["NUM_NODES"]


def test_num_edges():
    assert _int("NUM_EDGES") == EXPECT["NUM_EDGES"]


def test_reachable():
    assert _int("REACHABLE") == EXPECT["REACHABLE"]


def test_shortest():
    want = EXPECT["SHORTEST"]
    if want == "NONE":
        assert _word("SHORTEST") == "NONE"
    else:
        assert _int("SHORTEST") == want


def test_max_out_node():
    assert _word("MAX_OUT_NODE") == EXPECT["MAX_OUT_NODE"]


def test_max_out_degree():
    assert _int("MAX_OUT_DEGREE") == EXPECT["MAX_OUT_DEGREE"]


def test_has_cycle():
    assert _word("HAS_CYCLE") == EXPECT["HAS_CYCLE"]
