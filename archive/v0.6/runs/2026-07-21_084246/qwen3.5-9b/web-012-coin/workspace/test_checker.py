"""web-012-coin grader.

The render is judged from PIXELS, never from source: a model can write plausible
shader code that draws a flat grey disc. We pause the model's loop, step
window.demo.setTime across it, screenshot the hero canvas, and measure the
silhouette, the faces and the highlight.

Every test folds its own correctness in, so an empty or do-nothing submission
scores 0 rather than collecting free credit.
"""

import io
import math
import os
import re
from pathlib import Path

import pytest

APP = Path(__file__).parent / "app.html"

for _parent in Path(__file__).resolve().parents:
    _pw = _parent / ".pw-browsers"
    if _pw.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_pw)
        break

SZ = 160          # analysis resolution for silhouette/highlight work
N = 24            # frames sampled across the loop
SEASONS = re.compile(r"spring|summer|autumn|fall|winter", re.I)


def _luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


# Give each submission the renderer it needs — neither setting works for both.
# Default headless drops a non-trivial WebGL context (isContextLost(), blank
# canvas); forcing ANGLE fixes that but pushes canvas-2D onto the software
# rasteriser until it times out. So pick from the source: a page asking for a
# WebGL context gets ANGLE, a 2D page keeps the fast default. This hands the
# page a working browser; it does not grade it.
_GL_ARGS = ["--use-gl=angle", "--use-angle=swiftshader"]


def _wants_webgl() -> bool:
    try:
        src = APP.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"""getContext\(\s*["'](?:webgl2?|experimental-webgl)""",
                          src, re.I))


def _launch(p):
    args = _GL_ARGS if _wants_webgl() else []
    try:
        return p.chromium.launch(args=args)
    except Exception:
        return p.chromium.launch(channel="chromium", args=args)


@pytest.fixture(scope="module")
def ctx():
    assert APP.exists(), "app.html missing"
    from PIL import Image
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = _launch(p)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors, requests = [], []
        page.on("console",
                lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("request", lambda r: requests.append(r.url))
        page.goto(APP.as_uri())
        page.wait_for_timeout(600)
        # Halt the model's rAF loop up front: every pixel test steps setTime
        # itself, and a live loop would repaint between our two screenshots.
        # Best-effort - a missing API must fail test_demo_api, not every test.
        try:
            page.evaluate(
                "() => window.demo && window.demo.pause && window.demo.pause()")
        except Exception:
            pass
        state = {"page": page, "errors": errors, "requests": requests,
                 "Image": Image, "frames": None}
        yield state
        browser.close()


# ---------------------------------------------------------------- pixel helpers

def _shot(state, t):
    page, Image = state["page"], state["Image"]
    page.evaluate("t => window.demo.setTime(t)", t)
    raw = page.locator("#coin-hero").screenshot()
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _bbox(im, q=0.985):
    """Bound the COIN, not the backdrop.

    Thresholding colour-distance from a corner pixel looks obvious and is wrong:
    a model may paint a soft glow behind the hero, and the mask then bounds the
    GLOW - whose silhouette never changes - so a genuinely turning coin measures
    as static. gpt-5.6-luna did exactly that and scored 4/13 for a coin that
    turns, shines and is reeded (aspect spread read 0.009 instead of 0.337).

    A coin has HARD edges; a glow, by construction, does not. So bound the
    strong-gradient pixels: robust whatever the model paints behind, and it
    needs no extra promise from the prompt.
    """
    from PIL import ImageFilter
    g = im.convert("L").filter(ImageFilter.FIND_EDGES)
    px, (w, h) = g.load(), g.size
    vals = sorted(px[x, y] for y in range(h) for x in range(w))
    cut = max(vals[int(len(vals) * q)], 12)
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if px[x, y] >= cut:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _analyse(state):
    """Sample the loop once; cache. Per frame: bbox, area, aspect, highlight
    contrast + normalised highlight centroid, and a coarse face signature."""
    if state["frames"] is not None:
        return state["frames"]
    Image = state["Image"]
    state["page"].evaluate("() => window.demo.pause()")
    out = []
    for i in range(N):
        t = i / N
        full = _shot(state, t)
        im = full.resize((SZ, SZ), Image.BILINEAR)
        bb = _bbox(im)
        if not bb:
            out.append(None)
            continue
        x0, y0, x1, y1 = bb
        w, h = x1 - x0 + 1, y1 - y0 + 1
        px = im.load()
        # stats over the coin's own box, not a colour-keyed mask: whatever the
        # model paints behind the hero stays out of the numbers
        ls = sorted((_luma(px[x, y]), x, y)
                    for y in range(y0, y1 + 1) for x in range(x0, x1 + 1))
        med = ls[len(ls) // 2][0]
        p99 = ls[min(len(ls) - 1, int(len(ls) * 0.99))][0]
        top = ls[int(len(ls) * 0.95):] or ls[-1:]
        hx = sum(v[1] for v in top) / len(top)
        hy = sum(v[2] for v in top) / len(top)
        crop = im.crop((x0, y0, x1 + 1, y1 + 1)).resize((48, 48), Image.BILINEAR)
        cpx = crop.load()
        sig = [_luma(cpx[x, y]) for y in range(48) for x in range(48)]
        # relief = high-pass energy of the face INTERIOR. The specular is a
        # low-frequency lobe and blurs away; struck emblem/lettering survives.
        # Inset hard: the silhouette rim is itself a hard edge, and a plain flat
        # disc would otherwise score relief purely from its own outline.
        from PIL import ImageFilter
        ix, iy = int(w * 0.18), int(h * 0.18)
        inner = im.crop((x0 + ix, y0 + iy, x1 - ix + 1, y1 - iy + 1))
        if min(inner.size) >= 4:
            inner = inner.resize((48, 48), Image.BILINEAR)
            ipx = inner.load()
            iblur = inner.filter(ImageFilter.GaussianBlur(4)).load()
            relief = sum(abs(_luma(ipx[x, y]) - _luma(iblur[x, y]))
                         for y in range(48) for x in range(48)) / (48 * 48)
        else:
            relief = 0.0
        out.append({
            "t": t, "w": w, "h": h, "area": w * h,
            "aspect": w / max(1, h), "contrast": p99 - med,
            "hx": (hx - x0) / max(1, w), "hy": (hy - y0) / max(1, h),
            "sig": sig, "relief": relief, "bbox": bb, "full": full,
        })
    state["frames"] = out
    return out


def _live(state):
    fr = [f for f in _analyse(state) if f]
    assert len(fr) >= N * 0.8, \
        f"hero canvas renders nothing on {N - len(fr)}/{N} sampled frames"
    return fr


def _built(state):
    """Guard: an empty page has no external assets and no console errors either.
    Gate tests must not hand free credit to a do-nothing submission, so every
    one of them first proves something was actually built."""
    ok = state["page"].evaluate("""() => {
        const c = document.getElementById('coin-hero');
        const d = window.demo;
        return !!c && c.tagName === 'CANVAS'
               && !!d && typeof d.setTime === 'function';
    }""")
    assert ok, "no #coin-hero canvas with a window.demo API - nothing was built"


def _alive(state):
    """The task's core deliverable: a coin that TURNS and is METALLIC. Those are
    the two criteria a weak model fakes - a static fill dressed in plausible
    shader code.

    Everything else on this page (four tiles, a sold-out badge, an About
    paragraph) is trivial next to that, so none of it pays out on its own: a
    perfect site wrapped round a dead disc has not built the thing that was
    asked for. Same reasoning as the agentic tasks' _guards_intact().
    """
    _built(state)
    fr = _live(state)
    asp = [f["aspect"] for f in fr]
    spread = max(asp) - min(asp)
    shine = max(f["contrast"] for f in fr)
    assert spread >= 0.25 and shine >= 25.0, (
        f"no live coin: silhouette aspect spread {spread:.2f} (needs >=0.25, a "
        f"3D turn) and peak highlight {shine:.1f} luma over median (needs "
        f">=25, a metallic sheen). The hero is a flat or static disc, so the "
        "deliverable does not exist - nothing else on the page can score.")


# ---------------------------------------------------------------------- gates

def test_no_external_assets(ctx):
    _alive(ctx)
    src = APP.read_text(encoding="utf-8", errors="replace")
    bad = re.findall(r"""(?:src|href)\s*=\s*["']\s*(https?:|//)""", src, re.I)
    bad += re.findall(r"""url\(\s*["']?\s*(https?:|//)""", src, re.I)
    assert not bad, f"external asset reference(s) in source: {bad[:3]}"
    off = [u for u in ctx["requests"] if not u.startswith("file:")]
    assert not off, f"network request(s) made: {off[:3]}"


def test_no_console_errors(ctx):
    _alive(ctx)
    assert not ctx["errors"], f"console errors: {ctx['errors'][:3]}"


def test_demo_api(ctx):
    shape = ctx["page"].evaluate("""() => {
        const d = window.demo;
        const c = document.getElementById('coin-hero');
        return {
          demo: !!d && typeof d === 'object',
          setTime: !!d && typeof d.setTime === 'function',
          pause: !!d && typeof d.pause === 'function',
          canvasIsEl: !!d && !!d.canvas && d.canvas.tagName === 'CANVAS',
          heroExists: !!c && c.tagName === 'CANVAS',
        };
    }""")
    missing = [k for k, v in shape.items() if not v]
    assert not missing, f"window.demo contract incomplete: {missing}"


def test_settime_is_deterministic(ctx):
    _alive(ctx)
    a = _shot(ctx, 0.33).tobytes()
    b = _shot(ctx, 0.33).tobytes()
    assert a == b, "setTime(0.33) rendered different pixels on two calls - " \
                   "the loop must be a pure function of t"


# --------------------------------------------------------------- the render

def test_rotates_in_3d(ctx):
    """A disc spun in 2D keeps a constant silhouette; a disc turned in 3D does
    not. Aspect ratio must actually breathe across the loop. Drawing something
    of a sensible size, inside the canvas, is folded in here rather than paid
    for separately - it is a precondition, not an achievement."""
    fr = _live(ctx)
    big = max(f["area"] for f in fr)
    assert big > (SZ * SZ) * 0.04, \
        f"coin occupies only {big} px of the canvas - nothing meaningful drawn"
    # No margin assertion. The prompt asks for one and it makes measuring
    # easier, but it is OUR convenience, not a property of a good coin:
    # gpt-5.6-terra and deepseek-v4-pro drew large, excellent, plainly-turning
    # coins that fill the canvas and lost a point for it. If a coin were so
    # clipped we could not measure it, the aspect spread below would flatten and
    # fail on its own - which is the honest test.
    asp = [f["aspect"] for f in fr]
    spread = max(asp) - min(asp)
    assert spread >= 0.25, (
        f"silhouette aspect barely changes ({min(asp):.2f}..{max(asp):.2f}) - "
        "the coin is not turning in 3D")


def test_both_faces_are_struck(ctx):
    """Every face-on view must carry real relief - the front emblem and the back
    denomination. Catches a blank reverse and a flat disc.

    We deliberately do NOT assert the two faces show DIFFERENT motifs: that is
    not decidable from pixels. A coin turned 180 deg transforms its motif as
    much as a different motif would - measured on this very task, a same-motif
    control differed MORE from its own front (17.2 mean luma) than the
    two-real-faces reference did (15.0). Any threshold there would be noise, so
    we verify each face is actually struck rather than pretend to verify more.
    """
    fr = _live(ctx)
    big = max(f["area"] for f in fr)
    faceon = [f for f in fr if f["area"] >= 0.85 * big]
    assert len(faceon) >= 2, "never presents a face-on view"
    worst = min(f["relief"] for f in faceon)
    # 2.5, not 6: the question is struck-vs-blank, and blank measures ZERO (the
    # flat trap: 0.00). Measured struck faces span 5.6 (a subtle emboss) to 24.4
    # (a hard-struck one), so a 6.0 bar sat INSIDE the legitimate range and
    # failed a real coin for being tastefully understated. Calibrating a
    # threshold off one reference asserts every model emboss like ours does.
    assert worst >= 2.5, (
        f"the weakest face-on view carries only {worst:.1f} relief energy - "
        "a face is blank or unstruck (no emblem / no denomination)")


def test_specular_highlight_exists(ctx):
    """A flat/matte disc has no bright lobe above its own mid-tone."""
    fr = _live(ctx)
    best = max(f["contrast"] for f in fr)
    assert best >= 25.0, (
        f"peak highlight is only {best:.1f} luma above the coin's median - "
        "the surface reads as flat/matte, not metallic")


def test_specular_tracks_rotation(ctx):
    """A baked-in static gradient keeps its highlight in the same place on the
    coin; a real specular rakes across as it turns."""
    fr = _live(ctx)
    pts = [(f["hx"], f["hy"]) for f in fr]
    travel = max(math.dist(a, b) for a in pts for b in pts)
    assert travel >= 0.12, (
        f"highlight centroid moves only {travel:.3f} of the coin across the "
        "whole loop - the shine is painted on, not tracking the rotation")


def test_reeded_edge(ctx):
    """At the most edge-on frame the rim fills the silhouette; a reeded edge
    shows alternating ridge/groove banding along it, a smooth edge does not."""
    fr = _live(ctx)
    f = min(fr, key=lambda f: min(f["w"], f["h"]) / max(f["w"], f["h"]))
    im = f["full"]
    bb = _bbox(im)
    assert bb, "no silhouette at the edge-on frame"
    x0, y0, x1, y1 = bb
    px = im.load()
    if (x1 - x0) < (y1 - y0):          # thin vertically-standing rim
        cx = (x0 + x1) // 2
        prof = [_luma(px[cx, y]) for y in range(y0, y1 + 1)]
    else:                              # thin horizontally-lying rim
        cy = (y0 + y1) // 2
        prof = [_luma(px[x, cy]) for x in range(x0, x1 + 1)]
    assert len(prof) >= 40, "edge-on rim too small to inspect"
    w = 9
    det = []
    for i in range(len(prof)):
        lo, hi = max(0, i - w // 2), min(len(prof), i + w // 2 + 1)
        det.append(prof[i] - sum(prof[lo:hi]) / (hi - lo))
    changes = sum(1 for i in range(1, len(det))
                  if (det[i - 1] < -1.5 and det[i] > 1.5)
                  or (det[i - 1] > 1.5 and det[i] < -1.5))
    amp = max(det) - min(det)
    assert changes >= 5 and amp >= 12.0, (
        f"rim shows {changes} light/dark alternations (amplitude {amp:.1f}) - "
        "no reeding visible as the coin turns")


# ------------------------------------------------------------- site contract
# All of it gated on a live coin: this is a render task wearing a website, and
# four tiles plus a badge is not an achievement worth paying for on its own.

def test_four_editions(ctx):
    _alive(ctx)
    page = ctx["page"]
    keys = page.eval_on_selector_all(
        ".edition", "els => els.map(e => e.dataset.edition)")
    assert len(keys) == 4, f"expected exactly 4 .edition tiles, found {len(keys)}"
    assert sorted(k or "" for k in keys) == ["black", "bronze", "gold", "silver"], \
        f"data-edition values wrong: {keys}"


def test_edition_states(ctx):
    """One test for the whole availability contract: the two available editions
    sell, and neither unavailable one does."""
    _alive(ctx)
    page = ctx["page"]
    for key in ("bronze", "silver"):
        sel = f'.edition[data-edition="{key}"]'
        assert page.locator(sel).count() == 1, f"missing tile {key}"
        assert page.locator(sel).get_attribute("data-state") == "available", \
            f"{key} should be data-state=available"
        buy = page.locator(f"{sel} button.buy")
        assert buy.count() == 1, f"{key} has no button.buy"
        assert buy.first.is_enabled(), f"{key}'s buy control is disabled"
        buy.first.click()          # must not throw

    gold = '.edition[data-edition="gold"]'
    assert page.locator(gold).get_attribute("data-state") == "sold-out", \
        "gold must be data-state=sold-out"
    assert re.search(r"sold\s*out", page.locator(gold).inner_text(), re.I), \
        "gold tile never says SOLD OUT"
    assert page.eval_on_selector_all(
        f'{gold} button.buy', "els => els.filter(b => !b.disabled).length") == 0, \
        "gold is sold out but still has an enabled buy control"

    black = '.edition[data-edition="black"]'
    assert page.locator(black).get_attribute("data-state") == "coming-soon", \
        "black must be data-state=coming-soon"
    assert SEASONS.search(page.locator(black).inner_text()), \
        "black tile never names the season"
    assert page.eval_on_selector_all(
        f'{black} button.buy', "els => els.filter(b => !b.disabled).length") == 0, \
        "black is coming soon but still has an enabled buy control"


def test_edition_tiles_are_rendered(ctx):
    """Each tile must carry a real procedural render - not a flat placeholder."""
    from PIL import Image
    _alive(ctx)
    page = ctx["page"]
    tiles = page.locator(".edition canvas.edition-canvas")
    assert tiles.count() == 4, \
        f"expected 4 .edition-canvas elements, found {tiles.count()}"
    for i in range(4):
        raw = tiles.nth(i).screenshot()
        im = Image.open(io.BytesIO(raw)).convert("RGB").resize((64, 64))
        px = im.load()
        ls = [_luma(px[x, y]) for y in range(64) for x in range(64)]
        mean = sum(ls) / len(ls)
        sd = (sum((v - mean) ** 2 for v in ls) / len(ls)) ** 0.5
        assert sd >= 10.0, (
            f"edition tile {i} has luma stddev {sd:.1f} - reads as a flat "
            "placeholder, not a rendered coin")


def test_about_section(ctx):
    """The page must carry real prose about the mint - not just tiles and labels.

    Do NOT grep for the word "about": that tests a heading, not a section.
    gpt-5.6-terra headed its brand story "Made for the terminally online" and
    gpt-5.6-sol likewise; both wrote exactly what was asked for and both failed
    a test that was really asking them to use our noun. Verify there is a real
    paragraph of copy instead, which is the part a machine can honestly judge.
    """
    _alive(ctx)
    body = ctx["page"].inner_text("body")
    assert len(body) > 400, "page has almost no copy"
    paras = ctx["page"].eval_on_selector_all(
        "p, article, section div, li",
        "els => els.map(e => (e.innerText || '').trim().length)")
    assert paras and max(paras) >= 120, (
        f"no prose block over 120 chars (longest {max(paras) if paras else 0}) - "
        "the mint has no About copy, only labels")
