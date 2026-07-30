import re

from harness import config

SRC = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")

THEMES = {
    "dark":  dict(cell=(242, 242, 240), surface=(0x1a, 0x1a, 0x19),
                  ink=(0xff, 0xff, 0xff), flip=(0x0b, 0x0b, 0x0b)),
    "light": dict(cell=(22, 22, 26), surface=(0xfc, 0xfc, 0xfb),
                  ink=(0x0b, 0x0b, 0x0b), flip=(0xff, 0xff, 0xff)),
}


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lum(rgb):
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _composite(t, v):
    a = 0.10 + 0.90 * v
    return tuple(t["cell"][i] * a + t["surface"][i] * (1 - a) for i in range(3))


def _thresholds():
    box = re.search(r"function box\(v\)\{(.+?)\n", SRC).group(1)
    return {m.group(2): float(m.group(1))
            for m in re.finditer(r"v>=([\d.]+)\) c\+=' (flip-[dl])'", box)}


def test_the_flip_thresholds_are_the_measured_wcag_crossovers():
    got = _thresholds()
    assert set(got) == {"flip-d", "flip-l"}
    for theme, key in (("dark", "flip-d"), ("light", "flip-l")):
        t = THEMES[theme]
        crossover = next(i / 100 for i in range(101)
                         if _contrast(t["flip"], _composite(t, i / 100))
                         > _contrast(t["ink"], _composite(t, i / 100)))
        assert abs(got[key] - crossover) <= 0.01, (
            f"{key}={got[key]} but the {theme} crossover is {crossover}")


def test_every_score_number_stays_legible_across_the_whole_ramp():
    for theme, t in THEMES.items():
        key = "flip-d" if theme == "dark" else "flip-l"
        cutoff = _thresholds()[key]
        for i in range(101):
            v = i / 100
            fg = t["flip"] if v >= cutoff else t["ink"]
            c = _contrast(fg, _composite(t, v))
            assert c >= 4.4, f"{theme} score {v:.2f} contrast {c:.2f}"


def test_the_version_compare_containers_share_the_card_rule():
    rule = re.search(r"\n(\.card[^{]*)\{([^}]*)\}", SRC)
    selector, body = rule.group(1), rule.group(2)
    for cls in (".vc-cats", ".vc-members", ".vc-catdet"):
        assert cls in selector, f"{cls} is not on the shared container rule"
    assert "padding:2px 0" in body
    assert "border:1px solid var(--hair)" in body


def test_the_containers_do_not_redeclare_their_own_border():
    own = re.search(r"\n\.vc-cats, \.vc-members, \.vc-catdet \{([^}]*)\}", SRC).group(1)
    for prop in ("border", "background", "border-radius"):
        assert prop not in own, f"{prop} redeclared — it will drift from .card again"


def test_no_table_card_overrides_its_padding_inline():
    offenders = [m.group(0)[:90] for m in
                 re.finditer(r'class="card"[^>]*style="[^"]*padding[^"]*"\s*>\s*<table',
                             SRC)]
    assert not offenders, offenders


def test_both_themes_define_the_flipped_ink():
    assert SRC.count("--cell-ink:") == 2


def test_the_version_compare_wrapper_insets_its_content_horizontally():
    body = re.search(r"\n\.vc-wrap \{([^}]*)\}", SRC).group(1)
    pad = re.search(r"padding:\s*(\d+)px\s+(\d+)px", body)
    assert pad, f"vc-wrap must set a two-axis padding, got {body!r}"
    assert int(pad.group(2)) >= 12, (
        "the wrapper holds controls and prose that carry no padding of their "
        "own, so a card's default 0 horizontal inset leaves them on the border")


def test_every_version_compare_section_uses_the_padded_wrapper():
    plain = len(re.findall(r'<div class="card">\s*\n\s*<div class="vc-pick">', SRC))
    padded = len(re.findall(r'<div class="card vc-wrap">\s*\n\s*<div class="vc-pick">',
                            SRC))
    assert plain == 0, f"{plain} version-compare section(s) on a bare card"
    assert padded == 2, f"expected the model and family pages, found {padded}"


def test_the_inline_note_does_not_shift_itself_inside_a_flex_row():
    span = re.search(r"\n\.vc-note \{([^}]*)\}", SRC).group(1)
    assert "margin:0" in span.replace(" ", ""), (
        "a top margin on .vc-note drops the inline 'n task(s)' below its row")
    assert re.search(r"\np\.vc-note \{[^}]*margin:8px 0 0", SRC), (
        "the paragraph form still needs its leading gap")


def test_the_brand_is_self_contained_and_themeable():
    from harness import report
    assert report.BRAND_NAME == "Token Waster"
    assert report.BRAND_SVG.startswith("<svg")
    assert 'viewBox="0 0 32 32"' in report.BRAND_SVG, "square 32px footprint"
    assert "currentColor" in report.BRAND_SVG, "must theme for dark and light"
    assert "src=" not in report.BRAND_SVG, (
        "inlined on purpose: model/ and task/ pages sit one level down, so a "
        "file path would need per-page prefixing")
    assert 'aria-label="Token Waster"' in report.BRAND_SVG


def test_the_shared_shell_carries_its_own_narrow_override():
    from harness import report
    i = report.HEADER_CSS.index("max-width:var(--shell-w)")
    tail = report.HEADER_CSS[i:]
    assert "@media (max-width:760px)" in tail
    assert "padding:20px 15px 56px" in tail


def test_the_mobile_block_does_not_restate_the_body_padding():
    base = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    j = base.index(".topbar { flex-direction:column")
    window = base[max(0, j - 400):j]
    assert "body { padding:20px 15px 56px; }" not in window, (
        "two declarations of the narrow body padding; HEADER_CSS owns it")


def test_the_social_rail_links_only_confirmed_accounts():
    from harness import report
    urls = {name: url for name, url, _c, _p in report.SOCIALS}
    assert set(urls) == {"YouTube", "X", "TikTok", "Instagram", "GitHub"}
    for name, url in urls.items():
        assert url.startswith("https://"), name
        assert "tokenwaster" in url.lower(), f"{name} does not point at us: {url}"
    assert urls["GitHub"] == "https://github.com/tokenwaster", "profile, not repo"


def test_every_social_icon_carries_real_path_data():
    from harness import report
    for name, _u, colour, path in report.SOCIALS:
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", colour), name
        assert len(path) >= 190, f"{name} path looks hand-drawn ({len(path)} chars)"
        assert path.startswith("M"), name
        assert path.count(".") > 8, f"{name} lacks sub-pixel detail"


def test_the_rail_never_covers_the_reading_column():
    from harness import report
    css = report.HEADER_CSS
    assert ".srail { position:fixed" in css
    assert "right:calc((100vw - var(--shell-w)) / 2 - 52px)" in css
    assert "@media (max-width:1609px)" in css
    i = css.index("@media (max-width:1609px)")
    docked = css[i:i + 220]
    assert "bottom:18px" in docked and "flex-direction:row" in docked


def test_the_rail_is_injected_once_per_page():
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert 'class="srail"\' not in html' in src, (
        "the write hook must not double-inject when a page already has a rail")
    assert 'html.replace("</body>", _social_rail() + "</body>", 1)' in src


def test_a_tie_lists_every_model_not_just_the_first():
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert "_tied_disclosure" in src
    i = src.index("def _tied_disclosure")
    body = src[i:i + 700]
    assert "sorted(names, key=str.lower)" in body, "no implied ranking between ties"
    assert "_mlink(m)" in body, "each tied model must be a link"
    assert "{len(names)} tied" in body


def test_the_tie_list_opens_in_flow_so_it_cannot_be_clipped():
    assert ".tiepop .tp-list { display:flex; flex-direction:column" in SRC
    assert "position:absolute" not in SRC[SRC.index(".tiepop"):
                                          SRC.index(".tiepop") + 700], (
        "the fit table's card scrolls horizontally and clips positioned popups")
    assert "overflow-y:auto" in SRC[SRC.index(".tiepop .tp-list"):
                                    SRC.index(".tiepop .tp-list") + 300], (
        "a 40-model tie needs to scroll rather than run off the page")


def test_every_cohort_selector_on_the_overview_is_wired():
    for seg in ("standings", "fit", "valspeed", "bump", "podium"):
        assert f'data-seg="{seg}"' in SRC, f"{seg} selector missing"
        assert f"seg.dataset.seg === '{seg}'" in SRC, f"{seg} has no handler"


def test_version_rankings_reranks_inside_the_cohort():
    from harness import report
    td = {"t1": {"agg": {
        "loc": {"score": {"status": "scored", "score": 0.5}},
        "rem": {"score": {"status": "scored", "score": 0.9}},
    }}}
    vs = [("0.9", td, {"t1": None})]
    import unittest.mock as mock
    with mock.patch.object(report, "model_is_local",
                           side_effect=lambda m: m == "loc"):
        allr = report.version_rankings(vs)[0]["ranks"]
        loc = report.version_rankings(vs, cohort="local")[0]["ranks"]
        rem = report.version_rankings(vs, cohort="remote")[0]["ranks"]
    assert allr["rem"]["rank"] == 1 and allr["loc"]["rank"] == 2
    assert list(loc) == ["loc"] and loc["loc"]["rank"] == 1, (
        "a filtered chart must renumber, not keep all-models positions")
    assert list(rem) == ["rem"] and rem["rem"]["rank"] == 1


def test_the_podium_renumbers_and_remedals_when_filtered():
    i = SRC.index("function applyPodium(f)")
    js = SRC[i:i + 1100]
    assert "c.classList.remove('m1', 'm2', 'm3', 'm0')" in js, "stale medal"
    assert "rank++" in js and "'m' + rank" in js
    assert "c.dataset.partial === '1'" in js, (
        "a partial model is unranked in every cohort")
    assert "rank" in js.split("rank++")[0].split("let ")[1][:12]


def test_a_partial_model_is_never_medalled_in_any_cohort():
    i = SRC.index("function applyPodium(f)")
    js = SRC[i:i + 1100]
    part = js[js.index("dataset.partial === '1'"):]
    assert "return;" in part[:260], "partial must skip before rank++ increments"
    assert part.index("m0") < part.index("return;")


def test_the_cost_chart_has_no_local_variant_and_says_so():
    from harness import report
    assert 'cost_scatter = {"all": _cost_chart, "remote": _cost_chart, "local": ""}' \
        in SRC, "a local model's cost is electricity, not API spend"
    assert "No cost chart for local models" in SRC


def test_the_value_section_filters_both_charts_from_one_control():
    i = SRC.index('<div class="seg" data-seg="valspeed">')
    block = SRC[i:i + 1400]
    assert 'data-vcohort="{{ key }}"' in block
    assert "cost_scatter[key]" in block and "speed_scatter[key]" in block, (
        "the control previously governed only the speed chart")
