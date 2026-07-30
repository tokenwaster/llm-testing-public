import re

from harness import config

SRC = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")


def _block(start: str, length: int = 1400) -> str:
    i = SRC.index(start)
    return SRC[i:i + length]


def test_the_matrix_lens_sort_puts_partial_rows_last():
    js = _block("var scored=rows.map(function(r){")
    assert "p:r.classList.contains('partial')" in js
    assert "if(a.p!==b.p) return a.p?1:-1;" in js


def test_the_matrix_gap_is_measured_from_a_complete_row():
    js = _block("var scored=rows.map(function(r){")
    assert "var full=scored.filter(function(o){ return !o.p&&!isNaN(o.v); });" in js
    assert "var lead=full.length?full[0].v:NaN" in js


def test_the_matrix_never_ranks_or_leads_a_partial_row():
    js = _block("var scored=rows.map(function(r){")
    assert "rk.textContent=o.p?'—':String(rk_n)" in js
    assert "o.r.classList.toggle('lead', !o.p&&rk_n===1&&!isNaN(o.v))" in js


def test_the_standings_lens_sort_puts_partial_rows_last():
    js = _block("const isPart = tr => tr.dataset.partial === '1';")
    assert "if (pa !== pb) return pa ? 1 : -1;" in js


def test_the_standings_lens_leaves_a_partial_unranked():
    js = _block("let shown = 0, rank = 0, prev = null;")
    assert "if (isPart(tr)) {" in js
    assert "cell.textContent = '—';" in js
    assert re.search(r"shown\+\+;", js)


def test_a_partial_cannot_manufacture_a_tie():
    js = _block("let shown = 0, rank = 0, prev = null;")
    assert "&& !isPart(r) &&" in js


def test_the_column_sort_guard_is_still_there():
    assert "var pa = a.dataset.partial === '1', pb = b.dataset.partial === '1';" \
        in SRC


def test_the_server_leaves_a_partial_unranked_with_no_gap():
    assert '"rank": ("—" if _partial else _rk)' in SRC
    assert "gap_s, tied = \"—\", False" in SRC


def test_the_server_leader_is_drawn_from_complete_models_only():
    assert "_full = [m for m in _mrank if _cover[m] >= _n_suite]" in SRC
    i = SRC.index("_full = [m for m in _mrank")
    seg = SRC[i:i + 400]
    assert "for m in _full" in seg
    assert "for m in _mrank\n" not in seg


def test_the_server_rank_counter_skips_partial_rows():
    i = SRC.index("matrix_rows = []")
    seg = SRC[i:i + 400]
    assert "_rk = 0" in seg
    assert "if not _partial:" in seg and "_rk += 1" in seg


def test_the_rendered_overview_has_no_ranked_partial_row():
    idx = config.ROOT / "reports" / "index.html"
    if not idx.is_file():
        return
    html = idx.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'<div class="mx-row[^"]*\bpartial\b[^"]*"[^>]*>(.{0,400})',
                         html, re.S):
        rk = re.search(r'<span class="rk">([^<]*)</span>', m.group(1))
        assert rk and rk.group(1).strip() in ("—", ""), \
            f"a partial matrix row carries rank {rk.group(1)!r}"
        gp = re.search(r'<span class="gp">(.{0,24}?)</span>', m.group(1))
        if gp:
            assert "+-" not in gp.group(1), \
                f"partial row gap renders a negative as positive: {gp.group(1)!r}"
