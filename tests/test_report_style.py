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
