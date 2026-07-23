"""Static HTML reports, regenerated deterministically from runs/."""

import colorsys
import html
import re
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, BaseLoader

from . import config
from .util import read_json, read_jsonl

PALETTE_N = 24


def _hsl_hex(h_deg: float, s: float, lum: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h_deg % 360) / 360.0, lum, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def _overflow_palette(n: int = PALETTE_N - 8) -> tuple[str, str]:
    """Distinct theme-aware colours for slots 9..PALETTE_N via golden-angle hue
    rotation. Returns (dark_css, light_css) as `--s9:..;--s10:..;` fragments."""
    golden = 137.508
    dark, light = [], []
    for i in range(n):
        h = 68 + i * golden
        dark.append(f"--s{9 + i}:{_hsl_hex(h, 0.58, 0.62)};")
        light.append(f"--s{9 + i}:{_hsl_hex(h, 0.55, 0.42)};")
    return "".join(dark), "".join(light)


_EXTRA_DARK, _EXTRA_LIGHT = _overflow_palette()



_RUNS_BASE = config.RUNS_DIR
VRAM_REF_CTX = 32768
_PUBLIC_NAV = False

_NAV = [
    ("Overview", "index.html", False), ("Families", "family.html", False),
    ("Discriminate", "discriminate.html", False),
    ("Compare", "compare.html", False),
    ("Run", "/run", True), ("Watch", "/watch", True),
    ("Review", "/review", True),
    ("Backend", "/backend", True), ("Manage data", "/manage", True),
    ("Organize", "/families-edit", True),
    ("Info", "info.html", False),
]


def _nav(prefix: str = "") -> str:
    """Site nav for a page at the given relative `prefix` ('' at the report root,
    '../' under runs/ tasks/ models/). Control links drop in the public build."""
    out = []
    for label, href, control in _NAV:
        if control and _PUBLIC_NAV:
            continue
        target = href if control else prefix + href
        out.append(f'<a href="{target}">{label}</a>')
    return "<!--navlinks-->" + "".join(out) + "<!--/navlinks-->"



def load_run(run_dir: Path) -> dict | None:
    manifest = read_json(run_dir / "run.json")
    if not manifest:
        return None
    results = []
    for model_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        meta = read_json(model_dir / "model_meta.json", {})
        for task_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            metrics = read_json(task_dir / "metrics.json")
            score = read_json(task_dir / "score.json", {})
            if metrics:
                results.append({**metrics, "score": score, "model_meta": meta})
    return {"manifest": manifest, "results": results, "run_id": run_dir.name}


def load_all_runs(runs_dir: Path | None = None) -> list[dict]:
    runs_dir = runs_dir or config.RUNS_DIR
    if not runs_dir.exists():
        return []
    runs = [load_run(d) for d in sorted(runs_dir.iterdir()) if d.is_dir()]
    return [r for r in runs if r and r["results"]]




def fmt_ms(ms) -> str:
    if ms is None:
        return "—"
    return f"{ms / 1000:.1f}s" if ms >= 1000 else f"{ms:.0f}ms"


def fmt_span(ms) -> str:
    """Human duration for large totals: seconds under a minute, minutes under an
    hour, else hours. Per-task times keep fmt_ms."""
    if ms is None:
        return "—"
    s = ms / 1000
    if s < 60:
        return f"{s:.1f}s"
    if s < 3600:
        return f"{s / 60:.1f}m"
    return f"{s / 3600:.1f}h"


def fmt_cost(c) -> str:
    if c is None:
        return "—"
    if c == 0:
        return "$0"
    return f"${c:.4f}"


def fmt_tok(n) -> str:
    if n is None:
        return "—"
    return f"{n:,}"


def last_response_text(run_id: str, model: str, task: str, limit: int = 5000) -> str:
    """The model's final answer text, straight from the transcript."""
    events = read_jsonl(_RUNS_BASE / run_id / model / task / "transcript.jsonl")
    text = ""
    for ev in events:
        if ev.get("event") == "response" and ev.get("text"):
            text = ev["text"]
    if len(text) > limit:
        text = text[:limit] + f"\n…[truncated, {len(text) - limit} more chars in transcript]"
    return text


def score_state(s: dict) -> str:
    """good | warn | crit | pend — drives the status chip. Anything not
    scored (pending, skipped, missing) renders as pend."""
    if not s or s.get("status") != "scored" or s.get("score") is None:
        return "pend"
    v = s["score"]
    return "good" if v >= 0.8 else ("warn" if v >= 0.4 else "crit")


CHIP_SYMBOL = {"good": "✓", "warn": "◐", "crit": "✕", "pend": "◌"}


def chip(state: str, text: str, tip: str = "") -> str:
    """Status chip: symbol + text so state is never color-alone."""
    return (f'<span class="chip {state}" title="{html.escape(tip)}">'
            f'<i>{CHIP_SYMBOL[state]}</i>{html.escape(text)}</span>')


def _heat_swatch(v: float | None) -> str:
    """The matrix cell, reused inline: a square that ramps ink-opacity with the
    score (hollow when there's nothing scored). Same visual vocabulary as the
    overview grid so every score on the site reads the same way."""
    if v is None:
        return '<span class="hsw pend"></span>'
    a = 0.10 + 0.90 * max(0.0, min(1.0, v))
    return f'<span class="hsw" style="--a:{a:.3f}"></span>'


def score_chip(s: dict) -> str:
    st = score_state(s)
    tip = html.escape((s or {}).get("summary") or "")
    if st == "pend":
        text = "review" if (s or {}).get("status") == "pending" else "—"
        return (f'<span class="scv pend" title="{tip}">'
                f'{_heat_swatch(None)}{text}</span>')
    return (f'<span class="scv {st}" title="{tip}">'
            f'{_heat_swatch(s["score"])}<b>{_fmt_score(s["score"])}</b></span>')


_FAIL_BADGES = {
    "runaway": ("⟳ runaway", "#c90"),
    "timeout": ("⧖ timeout", "#c60"),
    "max_turns": ("⇥ max-turns", "#96c"),
    "error": ("⚠ error", "#c33"),
}


def _failure_mode_of(e: dict) -> str | None:
    """failure_mode from the metrics, or derived from attempts for runs written
    before the field existed (keeps old runs legible without a re-run)."""
    fm = e.get("failure_mode")
    if fm:
        return fm
    if e.get("status") == "max_turns":
        return "max_turns"
    atts = e.get("attempts") or []
    if not atts:
        return None
    last = atts[-1]
    if last.get("error_kind") == "runaway":
        return "runaway"
    sc = e.get("score") or {}
    failed = sc.get("status") != "scored" or (sc.get("score") or 0) == 0
    if last.get("stop_reason") == "length" and failed:
        return "runaway"
    if last.get("error_kind") == "timeout":
        return "timeout"
    if last.get("error_kind"):
        return "error"
    return None


def _fail_badge(e: dict) -> str:
    """Badge naming why a result failed, so a runaway reads differently from a
    wrong answer. Suppressed on a full pass."""
    sc = e.get("score") or {}
    if sc.get("status") == "scored" and sc.get("score") == 1.0:
        return ""
    fm = _failure_mode_of(e)
    if fm not in _FAIL_BADGES:
        return ""
    label, color = _FAIL_BADGES[fm]
    return (f'<span title="failure mode: {fm}" style="font-size:11px;'
            f'padding:1px 6px;border-radius:10px;border:1px solid {color};'
            f'color:{color};white-space:nowrap;margin-left:4px">{label}</span>')


def diagnose(e: dict, tdef, acfg: dict | None = None,
             suspect: dict | None = None) -> dict | None:
    """The reason a result went the way it did, via `assess.classify`:
    {category, attribution, detail}; None on a clean pass. The single source
    every page uses to explain a failure, so the wording never diverges."""
    if not tdef:
        return None
    from . import assess
    cls = assess.classify(e, tdef, acfg or assess.load_cfg(), suspect)
    return None if cls["category"] == "pass" else cls


def why_cell(cls: dict | None) -> str:
    """Compact HTML for a diagnosis: attribution badge + category, with the full
    detail on hover. '' for a clean pass."""
    if not cls:
        return ""
    attr = cls["attribution"]
    cat = cls["category"].replace("-", " ")
    return (f'<span class="attr attr-{attr}">{attr}</span> '
            f'<span title="{html.escape(cls["detail"])}">{html.escape(cat)}</span>')


def sparkline(values: list[float | None], width=140, height=34) -> str:
    """Inline SVG sparkline, 0..1 domain pinned so trends compare across rows."""
    pts = [(i, v) for i, v in enumerate(values) if v is not None]
    if not pts:
        return '<span class="muted">—</span>'
    n = max(len(values) - 1, 1)
    def xy(i, v):
        return (4 + i / n * (width - 8), height - 5 - v * (height - 10))
    path = " ".join(f"{'M' if k == 0 else 'L'}{xy(i, v)[0]:.1f},{xy(i, v)[1]:.1f}"
                    for k, (i, v) in enumerate(pts))
    dots = "".join(
        f'<circle cx="{xy(i, v)[0]:.1f}" cy="{xy(i, v)[1]:.1f}" r="2.5">'
        f'<title>run {i + 1}: {v:.2f}</title></circle>' for i, v in pts)
    base_y = height - 5
    return (f'<svg width="{width}" height="{height}" class="spark" role="img">'
            f'<line x1="4" y1="{base_y}" x2="{width - 4}" y2="{base_y}" class="axis"/>'
            f'<path d="{path}"/>{dots}</svg>')


def _slug_name(name: str) -> str:
    """Model name -> safe filename/anchor slug. Display keeps the real name."""
    import re
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-").lower() or "model"


def _mlink(name: str, prefix: str = "", cls: str = "mlink") -> str:
    """Model name linked to its summary page; `prefix` adjusts the relative path
    per page depth ('' from index, '../' from runs/tasks/models)."""
    return (f'<a class="{cls}" href="{prefix}models/{_slug_name(name)}.html">'
            f'{html.escape(name)}</a>')


def chart_legend(entries: list[dict], prefix: str = "") -> str:
    """Interactive right-side legend (colored dot + model name); hover highlights
    the model's marks in the sibling chart, click opens its page."""
    if not entries:
        return ""
    items = "".join(
        f'<a class="cl-item" data-m="{_slug_name(e["model"])}" '
        f'href="{prefix}models/{_slug_name(e["model"])}.html" '
        f'style="color:{e["color"]}">'
        f'<i style="background:{e["color"]}"></i>{html.escape(e["model"])}</a>'
        for e in entries)
    return f'<div class="clegend">{items}</div>'


def _nice_ceiling(v: float) -> float:
    """Round a max up to a clean axis top (1/2/5 × 10ⁿ) so ticks read well."""
    import math
    if v <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return m * mag
    return 10 * mag


def scatter(points: list[dict], width=1000, height=340) -> str:
    """Efficiency frontier: x = avg output tokens per task, y = avg score.
    One DOT per model; identity via the interactive right-legend + hover."""
    if not points:
        return ""
    pad_l, pad_r, pad_t, pad_b = 54, 20, 16, 40
    xmax = _nice_ceiling(max(p["x"] for p in points) * 1.1) or 1

    def X(x):
        return pad_l + x / xmax * (width - pad_l - pad_r)

    def Y(y):
        return pad_t + (1 - y) * (height - pad_t - pad_b)

    grid = "".join(
        f'<line x1="{pad_l}" y1="{Y(v):.1f}" x2="{width - pad_r}" '
        f'y2="{Y(v):.1f}" class="grid"/>'
        f'<text x="{pad_l - 8}" y="{Y(v) + 3.5:.1f}" class="tick" '
        f'text-anchor="end">{v:.1f}</text>' for v in (0.0, 0.25, 0.5, 0.75, 1.0))
    xticks = "".join(
        f'<text x="{X(xmax * k / 4):.1f}" y="{height - 22}" class="tick" '
        f'text-anchor="middle">{xmax * k / 4:,.0f}</text>' for k in range(5))
    dots = "".join(
        f'<g class="dot" data-m="{_slug_name(p["label"])}">'
        f'<circle class="hit" cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="14"/>'
        f'<circle class="mk" cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="6" '
        f'style="fill:{p.get("color", "var(--accent)")}"/>'
        f'<title>{html.escape(p["label"])}: score {p["y"]:.3f}, '
        f'{p["x"]:,.0f} tok/task</title></g>' for p in points)
    xlab = (f'<text x="{(pad_l + width - pad_r) / 2:.0f}" y="{height - 6}" '
            f'class="tick" text-anchor="middle">avg output tokens per task '
            f'— left is cheaper, up is better</text>')
    return (f'<svg viewBox="0 0 {width} {height}" class="scatter" role="img" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'style="width:100%;height:auto;display:block">'
            f'{grid}{xticks}{dots}{xlab}</svg>')


def _dominates(q: dict, p: dict, x_minimize: bool) -> bool:
    """q Pareto-dominates p: at-least-as-good on both axes, strictly better on
    one. y (score) is always maximised; x is minimised (cost) or maximised
    (speed) per `x_minimize`."""
    xb = (q["x"] <= p["x"]) if x_minimize else (q["x"] >= p["x"])
    xs = (q["x"] < p["x"]) if x_minimize else (q["x"] > p["x"])
    return xb and q["y"] >= p["y"] and (xs or q["y"] > p["y"])


def pareto_scatter(points: list[dict], x_label: str, *, x_minimize: bool,
                   x_fmt: str = "{:,.2f}", width: int = 1000,
                   height: int = 360) -> str:
    """Score (y, maximised) vs a cost/speed axis (x): draws the Pareto frontier
    and dims dominated dots. Dots carry data-tip for the shared hover JS; class
    matches the family scatter so both share one hover handler."""
    pts = [p for p in points if p.get("x") is not None and p.get("y") is not None]
    if len(pts) < 2:
        return ""
    for p in pts:
        p["dom"] = any(_dominates(q, p, x_minimize) for q in pts if q is not p)
    pad_l, pad_r, pad_t, pad_b = 52, 18, 16, 46
    xmax = max(p["x"] for p in pts) * 1.08 or 1
    ys = [p["y"] for p in pts]
    ymin = max(0.0, min(0.5, min(ys) - 0.05))

    def X(x):
        return pad_l + (x / xmax) * (width - pad_l - pad_r)

    def Y(y):
        return pad_t + (1 - (y - ymin) / (1 - ymin or 1)) * (height - pad_t - pad_b)

    parts = [f'<svg viewBox="0 0 {width} {height}" class="szchart" role="img" '
             f'preserveAspectRatio="xMidYMid meet" '
             f'style="width:100%;height:auto;display:block" aria-label="{x_label}">']
    for i in range(5):
        gy = ymin + (1 - ymin) * i / 4
        parts.append(f'<line x1="{pad_l}" y1="{Y(gy):.0f}" x2="{width - pad_r}" '
                     f'y2="{Y(gy):.0f}" stroke="var(--grid)" stroke-width="1"/>'
                     f'<text x="{pad_l - 6}" y="{Y(gy) + 4:.0f}" text-anchor="end" '
                     f'style="font:11px system-ui;fill:var(--muted)">{gy:.2f}</text>')
    for k in range(5):
        gx = xmax * k / 4
        parts.append(f'<text x="{X(gx):.0f}" y="{height - pad_b + 16:.0f}" '
                     f'text-anchor="middle" style="font:11px system-ui;'
                     f'fill:var(--muted)">{x_fmt.format(gx)}</text>')
    parts.append(f'<text x="{width / 2:.0f}" y="{height - 6:.0f}" text-anchor="middle" '
                 f'style="font:12px system-ui;fill:var(--ink-dim)">{html.escape(x_label)}</text>')
    front = sorted((p for p in pts if not p["dom"]), key=lambda p: p["x"])
    if len(front) > 1:
        d = " ".join(f'{"M" if i == 0 else "L"}{X(p["x"]):.0f},{Y(p["y"]):.0f}'
                     for i, p in enumerate(front))
        parts.append(f'<path d="{d}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="2" stroke-dasharray="5 4" opacity="0.75"/>')
    for p in pts:
        c = p.get("color", "var(--accent)")
        cx, cy = X(p["x"]), Y(p["y"])
        tip = p.get("tip") or f'{p["label"]} · {p["y"]:.3f}'
        r, op = (4, 0.4) if p["dom"] else (6, 1.0)
        parts.append(
            f'<circle class="szdot" cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="{c}" '
            f'opacity="{op}" data-tip="{html.escape(tip, quote=True)}" '
            f'style="cursor:pointer"/>')
    parts.append("</svg>")
    return "".join(parts)


_SCATTER_HOVER_JS = """<script>
(function(){
  var charts=[].slice.call(document.querySelectorAll('.szchart'));
  if(!charts.length) return;
  var tip=document.createElement('div'); tip.className='szttip';
  document.body.appendChild(tip);
  var R=16;
  charts.forEach(function(svg){
    var dots=[].slice.call(svg.querySelectorAll('.szdot')).map(function(c){
      return {cx:+c.getAttribute('cx'), cy:+c.getAttribute('cy'),
              tip:c.getAttribute('data-tip')};
    });
    if(!dots.length) return;
    svg.addEventListener('mousemove', function(e){
      var m=svg.getScreenCTM(); if(!m){ tip.style.display='none'; return; }
      var near=[];
      for(var i=0;i<dots.length;i++){ var d=dots[i];
        var sx=m.a*d.cx+m.c*d.cy+m.e, sy=m.b*d.cx+m.d*d.cy+m.f;
        var dist=Math.sqrt((sx-e.clientX)*(sx-e.clientX)+(sy-e.clientY)*(sy-e.clientY));
        if(dist<=R) near.push({dist:dist, tip:d.tip}); }
      if(!near.length){ tip.style.display='none'; return; }
      near.sort(function(a,b){ return a.dist-b.dist; });
      tip.innerHTML=near.map(function(o){ return o.tip; }).join('<br>');
      tip.style.display='block';
      var r=tip.getBoundingClientRect();
      var x=e.clientX+14, y=e.clientY+14;
      if(x+r.width>window.innerWidth-8) x=e.clientX-r.width-14;
      if(y+r.height>window.innerHeight-8) y=e.clientY-r.height-14;
      tip.style.left=x+'px'; tip.style.top=y+'px';
    });
    svg.addEventListener('mouseleave', function(){ tip.style.display='none'; });
  });
})();
</script>"""


def bar(value: float, vmax: float, width=140) -> str:
    """Thin magnitude bar, rounded data-end, hairline track."""
    w = 0 if vmax <= 0 else max(2, value / vmax * width)
    return (f'<span class="track" style="width:{width}px">'
            f'<span class="fill" style="width:{w:.0f}px"></span></span>')



BASE_CSS = """
:root {
  --plane:#0d0d0d; --surface:#1a1a19; --surface-2:#222220;
  --ink:#ffffff; --ink-2:#c3c2b7; --ink-dim:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --border:rgba(255,255,255,.10);
  --accent:#3987e5; --accent-soft:rgba(57,135,229,.16);
  --good:#0ca30c; --warn:#fab219; --crit:#d03b3b;
  /* editorial layer: hairline rules, a mono for data/labels, a matrix-cell ink
     ramp and the retrieval-miss orange — shared by every page's stat-line,
     tables and score grids so the whole suite reads as one thing */
  --hair:rgba(255,255,255,.07); --rule:rgba(255,255,255,.15);
  /* Matrix failure hues. --trap is NOT --warn: amber (#fab219) sits ~12 degrees
     from the retrieval-miss orange, so the two cells read as one colour in the
     grid. This yellow is ~23 degrees off it and much brighter, separating them
     by hue AND luminance. Kept separate from --warn because that token is text
     on the light theme, where a yellow this bright is unreadable. */
  --trap:#ffd60a; --miss:#d9600f; --cell-rgb:242,242,240;
  --mono:ui-monospace,"Cascadia Code","JetBrains Mono","SF Mono",Menlo,Consolas,monospace;
  /* categorical series — validated dark steps, fixed assignment order */
  --s1:#3987e5; --s2:#199e70; --s3:#c98500; --s4:#008300;
  --s5:#9085e9; --s6:#e66767; --s7:#d55181; --s8:#d95926;
  color-scheme: dark;
}
@media (prefers-color-scheme: light) {
  :root {
    --plane:#f9f9f7; --surface:#fcfcfb; --surface-2:#f2f1ed;
    --ink:#0b0b0b; --ink-2:#52514e; --ink-dim:#52514e; --muted:#898781;
    --grid:#e1e0d9; --border:rgba(11,11,11,.10);
    --accent:#2a78d6; --accent-soft:rgba(42,120,214,.12);
    --hair:rgba(20,20,26,.10); --rule:rgba(20,20,26,.20);
    /* A bright yellow cannot be bright AND visible on a near-white plane. Dark
       mode gets the vivid #ffd60a; here the hue does the separating (~25 deg
       off the orange) while the lightness drops far enough for the cell and its
       legend swatch to actually read against the page. */
    --trap:#a87f00; --miss:#b8460a; --cell-rgb:22,22,26;
    --s1:#2a78d6; --s2:#1baf7a; --s3:#eda100; --s4:#008300;
    --s5:#4a3aa7; --s6:#e34948; --s7:#e87ba4; --s8:#eb6834;
    color-scheme: light;
  }
}
* { box-sizing:border-box; }
body { background:var(--plane); color:var(--ink);
  font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;
  margin:0 auto; max-width:1480px; padding:32px 30px 72px; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
h1 { font-size:21px; font-weight:650; letter-spacing:-.01em; margin:0; }
.sub { color:var(--muted); font-size:12.5px; margin-top:4px; }
.reflink { display:inline-block; margin-left:10px; padding:1px 7px; border-radius:10px;
  border:1px solid var(--border); font-size:11.5px; text-decoration:none; white-space:nowrap; }
.reflink:hover { border-color:var(--accent); color:var(--accent); }
.topbar { display:flex; align-items:baseline; justify-content:space-between;
  gap:16px; flex-wrap:wrap; margin-bottom:22px; }
.nav a { margin-left:16px; font-size:13px; }
.tag { display:inline-block; background:var(--accent-soft); color:var(--accent);
  border-radius:20px; padding:2px 11px; font-size:11.5px; font-weight:600;
  margin-left:10px; vertical-align:2px; }
h2 { font-family:var(--mono); font-size:10.5px; font-weight:600; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); margin:34px 0 10px; }

/* hero stat-line — editorial, matches the overview masthead (no boxed tiles) */
.tiles { display:flex; flex-wrap:wrap; align-items:flex-end; row-gap:14px;
  margin:18px 0 6px; padding-bottom:16px; border-bottom:2px solid var(--ink); }
.tile { padding:0 22px; border-left:1px solid var(--hair); }
.tile:first-child { padding-left:0; border-left:none; }
.tile .v { font-size:27px; font-weight:750; letter-spacing:-.02em; line-height:1;
  font-variant-numeric:tabular-nums; }
.tile .v small { font-size:13px; color:var(--ink-2); font-weight:500; margin-left:2px; }
.tile .v .vsub { font-size:13px; color:var(--muted); font-weight:500; margin-left:5px;
  letter-spacing:0; }
.tile .k { font-family:var(--mono); font-size:10px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--muted); margin-top:7px; }

/* cards & tables */
.card { background:var(--surface); border:1px solid var(--hair);
  border-radius:6px; padding:2px 0; overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:13px;
  font-variant-numeric:tabular-nums; }
th { color:var(--muted); font-family:var(--mono); font-size:10px; font-weight:600;
  letter-spacing:.1em; text-transform:uppercase; text-align:left; padding:10px 14px 8px;
  border-bottom:1px solid var(--rule); white-space:nowrap; }
td { padding:8px 14px; border-bottom:1px solid var(--hair); vertical-align:middle; }
tr:last-child td { border-bottom:none; }
tbody tr:hover td { background:var(--surface-2); }
/* Data columns are CENTRED (header + cells aligned); text/name columns stay
   left. One site-wide rule — every table on every page reads the same. */
td.num, th.num, th[data-type="num"] { text-align:center; font-variant-numeric:tabular-nums; }
th[data-type="text"], td.model { text-align:left; }  /* names left; default td is already left */
td.nowrap, .nowrap { white-space:nowrap; }
.model { font-weight:600; }
.muted { color:var(--muted); }
/* the dynamic "Ranked by" column on the standings — tinted so it's clear the
   order follows it; its header label + cells are set by the lens JS */
th.lenscol, td.lensval { background:var(--accent-soft); font-weight:600; }
/* scatter chrome (score-vs-cost/speed/VRAM) — shared by overview + family */
.chartkey { display:flex; flex-wrap:wrap; align-items:center; gap:6px 16px;
  font-size:12px; color:var(--ink-dim); margin:2px 0 6px; }
.chartkey .k-dot { display:inline-block; width:10px; height:10px; border-radius:50%;
  background:var(--accent); vertical-align:-1px; margin-right:2px; }
.chartkey .k-dot.dim { opacity:.4; }
.chartkey .k-line { display:inline-block; width:26px; border-top:2px dashed var(--accent);
  vertical-align:4px; margin:0 2px 0 6px; }
/* aggregated hover tooltip — lists every dot under the cursor */
.szttip { position:fixed; z-index:60; pointer-events:none; display:none;
  background:var(--surface); border:1px solid var(--border); border-radius:8px;
  padding:6px 9px; font-size:12px; line-height:1.5; color:var(--ink);
  box-shadow:0 6px 20px rgba(0,0,0,.35); max-width:300px; }
.szttip b { color:var(--ink); }
/* click-to-sort tables */
table.sortable th[data-type] { cursor:pointer; user-select:none; white-space:nowrap; }
table.sortable th[data-type]:hover { color:var(--ink); }
table.sortable th .caret { opacity:0; font-size:9px; margin-left:5px;
  vertical-align:1px; }
table.sortable th[data-type]:hover .caret { opacity:.4; }
table.sortable th.sorted .caret { opacity:1; color:var(--accent); }
.fitpick { font-weight:650; color:var(--good); white-space:nowrap; }
.fitval { font-weight:600; color:var(--accent); white-space:nowrap; }
.small { font-size:11.5px; color:var(--muted); }
/* attribution badges — who's at fault for a failure/retry */
.attr { display:inline-block; font-size:10.5px; font-weight:700;
  letter-spacing:.04em; text-transform:uppercase; border-radius:6px;
  padding:1px 7px; white-space:nowrap; }
.attr-model { background:var(--surface-2); color:var(--ink-2);
  border:1px solid var(--border); }
.attr-harness { background:var(--crit); color:#fff; }
.attr-infra { background:var(--accent-soft); color:var(--accent); }
.attr-known-limit { background:transparent; color:var(--muted);
  border:1px dashed var(--muted); }
.attr-clean { background:var(--good); color:#fff; }
.rollup { display:flex; gap:8px; flex-wrap:wrap; align-items:center;
  margin:2px 0 8px; font-size:12px; }
.rollup .pill { background:var(--surface-2); border:1px solid var(--border);
  border-radius:20px; padding:2px 11px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; }
.rollup .pill b { color:var(--ink); }
/* model-name links — clickable everywhere, take you to the model page */
a.mlink { color:inherit; font-weight:600; text-decoration:none;
  border-bottom:1px dotted var(--border); }
a.mlink:hover { color:var(--accent); border-bottom-color:var(--accent);
  text-decoration:none; }

/* status chips — symbol + text, never color alone */
.chip { display:inline-flex; align-items:center; gap:6px; font-weight:600;
  font-variant-numeric:tabular-nums; white-space:nowrap; }
.chip i { font-style:normal; font-size:11px; width:17px; height:17px; line-height:17px;
  border-radius:50%; text-align:center; flex:none; }
.chip.good i { background:var(--good); color:#fff; }
.chip.warn i { background:var(--warn); color:#0b0b0b; }
.chip.crit i { background:var(--crit); color:#fff; }
.chip.pend i { background:transparent; color:var(--muted);
  border:1.5px dashed var(--muted); line-height:14px; }
.chip.pend { color:var(--muted); font-weight:500; }

/* score cells — the matrix swatch reused inline: a score-ramped square + the
   number, so every grid on the site (categories, per-task, score grid, model
   comparison) reads like the overview hero. The number is tinted good/warn/crit
   so the state never rides on colour alone. */
.scv { display:inline-flex; align-items:center; font-variant-numeric:tabular-nums;
  white-space:nowrap; }
.scv b { font-weight:600; }
.scv.warn b { color:var(--warn); }
.scv.crit b { color:var(--crit); }
.scv.pend { color:var(--muted); font-weight:500; }
.hsw { display:inline-block; width:11px; height:11px; border-radius:2px; flex:none;
  margin-right:7px; background:rgba(var(--cell-rgb),var(--a,.2)); }
.hsw.pend { background:transparent; box-shadow:inset 0 0 0 1px var(--hair); }
/* head-to-head compare page */
.cmp-pick { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:6px 0 22px; }
.cmp-sel { flex:1 1 260px; min-width:200px; font-size:15px; font-weight:600;
  padding:9px 12px; border-radius:8px; border:1px solid var(--border);
  background:var(--surface); color:var(--ink); font-family:inherit; }
.cmp-swap { flex:none; font-size:18px; line-height:1; padding:8px 12px; cursor:pointer;
  border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--ink); }
.cmp-swap:hover { border-color:var(--accent); color:var(--accent); }
.cmp-head { margin:0 0 28px; overflow-x:auto; }
.cmp-tbl { border-collapse:collapse; width:100%; }
.cmp-tbl th, .cmp-tbl td { padding:9px 14px; text-align:center; border-bottom:1px solid var(--hair); }
.cmp-tbl thead th { font-size:15px; font-weight:700; border-bottom:1px solid var(--rule); }
.cmp-tbl thead th a { font-weight:700; }
.cmp-k { text-align:left !important; font-family:var(--mono); font-size:11px;
  letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.cmp-c { font-variant-numeric:tabular-nums; font-size:15px; }
.cmp-c.win { color:var(--good); font-weight:750; }
.cmp-d { font-family:var(--mono); font-size:11.5px; color:var(--muted); min-width:64px; }
.cmp-cat { margin:0 0 18px; }
.cmp-cath { font-family:var(--mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); padding:6px 0 4px; border-bottom:1px solid var(--rule); margin-bottom:4px; }
.cmp-row { display:grid; grid-template-columns:1fr 90px 96px 90px; align-items:center;
  gap:10px; padding:3px 4px; border-bottom:1px solid var(--hair); }
.cmp-row:hover { background:var(--surface); }
.cmp-t { font-size:12.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cmp-row .scv { justify-content:flex-start; font-variant-numeric:tabular-nums; }
.cmp-row .scv.ra { justify-content:flex-end; }
.cmp-row .scv.ra .hsw { margin-right:0; margin-left:7px; }
.cmp-dc { text-align:center; }
.cmp-td { font-family:var(--mono); font-size:11px; white-space:nowrap; }
.cmp-td.ga { color:var(--good); } .cmp-td.gb { color:var(--accent); }
.cmp-td.tie { color:var(--muted); }

/* marks */
.spark path { fill:none; stroke:var(--accent); stroke-width:2;
  stroke-linecap:round; stroke-linejoin:round; }
.spark circle { fill:var(--accent); }
.spark .axis { stroke:var(--grid); stroke-width:1; }
.track { display:inline-block; height:8px; background:var(--surface-2);
  border-radius:4px; vertical-align:middle; overflow:hidden; }
.fill { display:block; height:8px; background:var(--accent);
  border-radius:0 4px 4px 0; }

/* chart + right-legend layout */
.chartcard { padding:16px 18px; overflow:hidden; }
.chartwrap { display:flex; gap:18px; align-items:stretch; }
.chartsvg { flex:1 1 auto; min-width:0; }
.clegend { flex:0 0 auto; width:210px; max-height:340px; overflow-y:auto;
  display:flex; flex-direction:column; gap:1px; align-self:center;
  border-left:1px solid var(--grid); padding-left:14px; }
.cl-item { display:flex; align-items:center; gap:8px; font-size:12px;
  font-weight:600; padding:3px 5px; border-radius:6px; text-decoration:none;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:pointer; }
.cl-item i { flex:none; width:11px; height:11px; border-radius:50%; }
.cl-item:hover { background:var(--surface-2); text-decoration:none; }
@media (max-width:900px) { .chartwrap { flex-direction:column; }
  .clegend { flex-flow:row wrap; width:auto; border-left:0; border-top:1px
  solid var(--grid); padding:12px 0 0; max-height:none; } }
/* Phones / narrow tablets: tighter gutters, and EVERY table becomes its own
   horizontal scroller — display:block keeps the grid intact (anonymous table
   boxes reconstruct rows/cells) so no page can overflow sideways, even a table
   that isn't wrapped in a .card. Verified 375px: family/info overflow → 0. */
@media (max-width:760px) {
  body { padding:20px 15px 56px; }
  h1 { font-size:19px; }
  /* stack the header so the menu gets the full width and its links wrap
     instead of overflowing (the nav is a flex item that otherwise sizes to
     its one-line max-content). */
  .topbar { flex-direction:column; align-items:flex-start; gap:8px; }
  .nav { display:flex; flex-wrap:wrap; row-gap:4px; }
  .nav a { margin-left:0; margin-right:15px; }
  table { display:block; overflow-x:auto; -webkit-overflow-scrolling:touch;
    max-width:100%; }
}

/* shared chart chrome */
.grid, .scatter .grid { stroke:var(--grid); stroke-width:1; }
.tick, .scatter .tick { fill:var(--muted); font-size:10px;
  font-variant-numeric:tabular-nums; }

/* rankings bump chart — hover a bubble to light up every tied model */
.bump .bm { transition:opacity .1s; }
.bump .bmhit, .bump .bmlabel { cursor:pointer; }
.bump.focus .bm { opacity:.12; }
.bump.focus .bm.on { opacity:1; }

/* dot marks — the only chart geometry now */
.dot .hit { fill:transparent; }
.dot .mk { stroke:var(--surface); stroke-width:2; transition:opacity .1s; }
.dot:hover .mk { stroke:var(--ink); stroke-width:2.5; }
/* legend-hover focus: dim everyone but the hovered model */
.chartwrap.focus .dot .mk { opacity:.13; }
.chartwrap.focus .dot.on .mk { opacity:1; }
.clegend.focus .cl-item { opacity:.35; }
.clegend.focus .cl-item.on { opacity:1; }

/* leaderboard podium — clickable placards, medal accents for the top 3 */
.podium { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:12px; margin:18px 0 4px; }
.pcard { display:block; background:var(--surface); border:1px solid var(--hair);
  border-left:3px solid var(--hair); border-radius:6px; padding:15px 18px 15px;
  color:inherit; text-decoration:none; position:relative;
  transition:transform .1s, box-shadow .1s; }
.pcard:hover { text-decoration:none; transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(0,0,0,.18); }
.pcard.m1 { border-left-color:#e8b923; }
.pcard.m2 { border-left-color:#a9b0b8; }
.pcard.m3 { border-left-color:#c8813f; }
.pcard .rank { font-family:var(--mono); font-size:10px; color:var(--muted);
  letter-spacing:.1em; text-transform:uppercase; font-weight:600; }
.pcard.m1 .rank { color:#e8b923; } .pcard.m2 .rank { color:#a9b0b8; }
.pcard.m3 .rank { color:#c8813f; }
.pcard .name { font-weight:650; font-size:15px; margin:3px 0 10px;
  word-break:break-word; }
.pcard:hover .name { color:var(--accent); }
.pcard .score { font-size:34px; font-weight:750; letter-spacing:-.02em;
  line-height:1; font-variant-numeric:tabular-nums; }
.pcard .score small { font-size:13px; font-weight:500; color:var(--muted); }
.pcard .score .pci { font-size:12px; font-weight:500; color:var(--muted);
  margin-left:6px; letter-spacing:0; }
.pcard .subs { font-size:11.5px; color:var(--muted); margin-top:11px;
  line-height:1.75; }
.pcard .subs b { color:var(--ink-2); font-variant-numeric:tabular-nums; }
.pcard .cardarrow { position:absolute; top:14px; right:15px; color:var(--muted);
  font-size:13px; opacity:0; transition:opacity .1s; }
.pcard:hover .cardarrow { opacity:1; }

/* callouts & details */
.delrun { background:transparent; border:none; color:var(--muted);
  cursor:pointer; font-size:13px; }
.delrun:hover { color:var(--crit); }
.warnbox { background:var(--surface); border:1px solid var(--warn);
  border-radius:10px; padding:12px 16px; font-size:12.5px; margin:14px 0;
  color:var(--ink-2); }
.warnbox b { color:var(--ink); }
details.det { background:var(--surface); border:1px solid var(--border);
  border-radius:10px; margin:8px 0; padding:0 16px; }
details.det summary { cursor:pointer; padding:11px 0; color:var(--ink-2);
  font-size:13px; list-style:none; display:flex; gap:10px; align-items:center; }
details.det summary::before { content:"›"; color:var(--muted);
  transition:transform .12s; }
details.det[open] summary::before { transform:rotate(90deg); }
details.det .inner { padding:2px 0 14px; }
/* the row + details a matrix cell linked to (#m-<model>) */
details.det.hit { border-color:var(--accent); box-shadow:0 0 0 1px var(--accent); }
tr.hit > td { background:var(--surface); }
tr.hit > td:first-child { box-shadow:inset 2px 0 0 var(--accent); }
a.filelink { font-family:var(--mono); font-size:11px; color:var(--muted);
  border:1px solid var(--hair); border-radius:4px; padding:2px 6px; white-space:nowrap; }
a.filelink:hover { color:var(--accent); border-color:var(--accent); }
/* a number built from more than one run says so */
.sig { font-family:var(--mono); font-size:10px; color:var(--muted); margin-left:5px; }
.nrun { font-family:var(--mono); font-size:10px; color:var(--accent);
  border:1px solid var(--hair); border-radius:3px; padding:0 3px; cursor:help; }
.snote { display:block; font-family:var(--mono); font-size:9.5px; color:var(--muted);
  letter-spacing:.03em; }
.hardmark { color:var(--accent); }
/* version-over-version compare (model + family pages) */
.vc-pick { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:10px; font-size:12px;
  color:var(--muted); align-items:center; }
.vc-pick select { background:var(--plane); color:var(--fg); border:1px solid var(--grid);
  border-radius:5px; padding:3px 7px; font-size:12px; margin-left:4px; }
.vc-sum { font-size:13.5px; margin:4px 0 14px; }
.vc-cell { display:inline-block; min-width:36px; text-align:center; font-family:var(--mono);
  font-size:11px; border-radius:3px; padding:2px 4px; margin-right:3px;
  border:1px solid var(--hair); }
.vc-d { font-family:var(--mono); font-size:11px; font-weight:600; padding:1px 5px;
  border-radius:3px; margin:0 8px; }
.vc-d.up { color:#1f9d55; } .vc-d.down { color:var(--crit); } .vc-d.flat { color:var(--muted); }
.vc-verd { font-size:10px; text-transform:uppercase; letter-spacing:.05em; padding:1px 6px;
  border-radius:3px; border:1px solid var(--hair); }
.vc-verd.better { color:#1f9d55; border-color:#1f9d55; }
.vc-verd.worse { color:var(--crit); border-color:var(--crit); }
.vc-catrow, .vc-taskrow { display:flex; align-items:center; gap:2px; padding:2px 0; font-size:12px; }
.vc-cat { min-width:130px; color:var(--muted); font-size:11px; }
.vc-cats { margin:8px 0 4px; }
.vc-catdet > summary { cursor:pointer; padding:6px 0; color:var(--ink-2); font-size:12px;
  list-style:none; }
.vc-catdet > summary::before { content:"›"; color:var(--muted); margin-right:6px; }
.vc-catdet[open] > summary::before { content:"⌄"; }
.vc-note { color:var(--muted); font-size:11px; margin:8px 0 0; }
.vc-warn { color:var(--trap); font-size:10px; margin-left:6px; }
pre { background:var(--plane); border:1px solid var(--grid); padding:10px 12px;
  border-radius:8px; font-size:12px; overflow-x:auto; white-space:pre-wrap;
  color:var(--ink-2); }
.foot { margin-top:36px; font-size:11.5px; color:var(--muted); line-height:1.7;
  border-top:1px solid var(--grid); padding-top:14px; }
code { background:var(--surface-2); border-radius:4px; padding:1px 6px;
  font-size:12px; }
"""

BASE_CSS = BASE_CSS.replace(
    "--s8:#d95926;", "--s8:#d95926;" + _EXTRA_DARK).replace(
    "--s8:#eb6834;", "--s8:#eb6834;" + _EXTRA_LIGHT)

_MATRIX_CSS = """
.mx-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; margin-top:12px; padding-bottom:6px; }
.mx { min-width:max-content; }
.mx-row { display:flex; align-items:stretch; }
.mx-rail { flex:0 0 300px; display:grid; grid-template-columns:26px 1fr auto auto;
  align-items:center; column-gap:10px; padding:0 14px 0 2px; height:29px;
  border-bottom:1px solid var(--hair); }
.mx-row.head .mx-rail { align-items:end; height:auto; padding-bottom:7px;
  border-bottom:1px solid var(--rule); }
.mx-row:hover:not(.head):not(.foot) .mx-rail,
.mx-row:hover:not(.head):not(.foot) .mx-cells { background:var(--surface); }
.mx-rail .rk { font-family:var(--mono); font-size:11.5px; color:var(--muted); text-align:right;
  font-variant-numeric:tabular-nums; }
.mx-rail .nm { font-size:12.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mx-rail .nm a { font-weight:600; }
.mx-rail .sc { font-family:var(--mono); font-size:12px; font-weight:600; text-align:right;
  font-variant-numeric:tabular-nums; }
.mx-rail .sc .ci { font-weight:400; font-size:9.5px; color:var(--muted); margin-left:3px;
  vertical-align:1px; }
.mx-rail .gp { font-family:var(--mono); font-size:11px; color:var(--muted); text-align:right;
  min-width:44px; font-variant-numeric:tabular-nums; }
.mx-rail .gp .tie { color:var(--accent); font-weight:700; margin-right:2px; cursor:help; }
.mx-row.lead .mx-rail { box-shadow:inset 3px 0 0 var(--accent); }
.mx-row.lead .rk, .mx-row.lead .sc, .mx-row.lead .gp { color:var(--accent); }
.mx-row.head .rk, .mx-row.head .nm, .mx-row.head .sc, .mx-row.head .gp { color:var(--muted);
  font-family:var(--mono); font-size:9.5px; letter-spacing:.1em; text-transform:uppercase; }
.mx-cells { display:flex; gap:14px; align-items:center; padding:0 8px; height:29px;
  border-bottom:1px solid var(--hair); }
.mx-row.head .mx-cells { align-items:end; height:auto; padding-bottom:7px;
  border-bottom:1px solid var(--rule); }
.mx-grp { display:grid; grid-auto-flow:column; gap:3px; }
.mx-cell { width:15px; height:15px; border-radius:2px; display:block;
  cursor:pointer; transition:transform .08s, box-shadow .08s; }
.mx-cell:hover { transform:scale(1.28); box-shadow:0 0 0 1.5px var(--fg);
  position:relative; z-index:2; }
.mx-cell.pass { background:rgba(var(--cell-rgb),var(--a,.2)); }
.mx-cell.trap { background:var(--trap); }
.mx-cell.dnf { background:var(--crit); }
.mx-cell.miss { background:var(--miss); }
.mx-cell.na { background:transparent; box-shadow:inset 0 0 0 1px var(--hair); }
.mx-clabel { font-family:var(--mono); font-size:9px; letter-spacing:.03em; text-transform:uppercase;
  color:var(--ink-2); white-space:nowrap; overflow:hidden; text-overflow:clip; }
.mx-clabel .cn { color:var(--muted); }
.mx-row.foot .mx-rail, .mx-row.foot .mx-cells { border-bottom:none; border-top:1px solid var(--rule);
  height:32px; }
.mx-row.foot .fl { grid-column:1/-1; text-align:right; font-family:var(--mono); font-size:10px;
  letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.mxlegend { display:flex; flex-wrap:wrap; gap:8px 20px; margin-top:16px; font-size:12px;
  color:var(--ink-2); align-items:center; }
.mxlegend .grp { display:flex; align-items:center; gap:7px; }
.mxlegend .ramp { display:flex; gap:2px; }
.mxlegend .ramp i { width:13px; height:13px; border-radius:2px; background:rgba(var(--cell-rgb),var(--a)); }
.mxlegend .sw { width:13px; height:13px; border-radius:2px; display:inline-block; }
.mxlegend .sw.na { background:transparent; box-shadow:inset 0 0 0 1px var(--hair); }
.mxlegend .k { font-family:var(--mono); font-size:10px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--muted); }
/* segmented toggle (All/Hard/Easy subset pickers) — overview + discriminate */
.seg { display:inline-flex; gap:0; margin:4px 0 10px; border:1px solid var(--border);
  border-radius:9px; overflow:hidden; }
.seg button { background:var(--surface); color:var(--ink-dim); border:0;
  border-right:1px solid var(--border); padding:5px 13px; font:inherit;
  font-size:12.5px; cursor:pointer; }
.seg button:last-child { border-right:0; }
.seg button.on { background:var(--accent); color:#fff; }
"""
BASE_CSS += _MATRIX_CSS

RUN_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Run {{ run_id }} · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">
  <div><h1>Run {{ run_id }}{% if manifest.tag %}<span class="tag">{{ manifest.tag }}</span>{% endif %}</h1>
  <div class="sub">{{ manifest.started }} → {{ manifest.finished or "…" }}{% if env_line %} · {{ env_line }}{% endif %}</div></div>
  <div class="nav">{{ nav }}</div>
</div>

<div class="tiles">
{% for t in tiles %}<div class="tile"><div class="v">{{ t.v }}{% if t.sub %}<span class="vsub" title="{{ t.sub_tip }}">{{ t.sub }}</span>{% endif %}</div><div class="k">{{ t.k }}</div></div>
{% endfor %}</div>

{% if run_rollup %}
<div class="rollup" style="margin-top:14px">
  <span class="muted">failures:</span>
  {% for a in run_rollup.pills %}<span class="pill"><span class="attr attr-{{ a.cls }}">{{ a.name }}</span> {{ a.n }}</span>{% endfor %}
  {% if not run_rollup.pills %}<span class="pill">none</span>{% endif %}
  <span class="pill">retries <b>{{ run_rollup.recovered }}</b> recovered · <b>{{ run_rollup.fatal }}</b> fatal</span>
</div>
{% endif %}

<h2>Models · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Model</th><th data-type="num">Score</th><th class="num" data-type="num">First-try</th><th class="num" data-type="num">Errors</th>
<th class="num" data-type="num">Wall</th><th class="num" data-type="num">TTFT</th><th class="num" data-type="num">Gen tok/s</th>
<th class="num" data-type="num">Tokens in / out</th><th class="num" data-type="num">Cost</th><th class="num" data-type="num">Retries</th>
<th class="num">Cold start</th><th class="num">Energy</th></tr>
{% for s in summaries %}
<tr><td>{{ s.model_link }}</td><td>{{ s.chip }}</td>
<td class="num">{{ s.first_try }}</td><td class="num">{{ s.errors }}</td>
<td class="num">{{ s.wall }}</td><td class="num">{{ s.ttft }}</td>
<td class="num">{{ s.tps }}</td><td class="num">{{ s.tokens }}</td>
<td class="num">{{ s.cost }}</td><td class="num">{{ s.retries }}</td>
<td class="num">{{ s.cold }}</td><td class="num">{{ s.energy }}</td></tr>
{% endfor %}</table></div>

<h2>Score grid</h2>
<div class="card"><table>
<tr><th>Task</th><th>Category</th>
{% for m in models %}<th class="num">{{ m }}</th>{% endfor %}</tr>
{% for row in grid %}
<tr><td class="model">{% if row.linked %}<a href="../tasks/{{ row.task }}.html">{{ row.task }}</a>{% else %}{{ row.task }}{% endif %}</td>
<td class="small">{{ row.cat }} · tier {{ row.tier }}</td>
{% for c in row.cells %}<td class="num">{{ c.chip }}<div class="small">{{ c.time }}{% if c.tok %} · {{ c.tok }}{% endif %}</div></td>{% endfor %}
</tr>
{% endfor %}</table></div>

<h2>Attempt detail</h2>
{% for d in details %}
<details class="det"><summary><b>{{ d.model }}</b> / {{ d.task }} — {{ d.summary }}</summary>
<div class="inner">
<table><tr><th class="num">#</th><th class="num">TTFT</th><th class="num">Total</th>
<th class="num">Tok in</th><th class="num">Tok out</th><th>Stop</th><th>Error</th></tr>
{% for a in d.attempts %}
<tr><td class="num">{{ a.n }}</td><td class="num">{{ a.ttft }}</td>
<td class="num">{{ a.total }}</td><td class="num">{{ a.tin }}</td>
<td class="num">{{ a.tout }}</td><td>{{ a.stop }}</td><td class="small">{{ a.err }}</td></tr>
{% endfor %}</table>
{% if d.detail %}<pre>{{ d.detail }}</pre>{% endif %}
<div class="small">transcript: <code>{{ d.path }}</code></div>
</div></details>
{% endfor %}

<div class="foot">Wall times include every retry. Token counts come from each
provider's usage field — never estimated. Gen tok/s = completion tokens ÷
generation time (excludes time-to-first-token).</div>
{{ sort_js }}
</body></html>"""

TASK_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ task_id }} · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">
  <div><h1>{{ title }}<span class="tag">{{ category }} · tier {{ tier }}</span></h1>
  <div class="sub">{{ task_id }} · scoring: {{ scoring_type }} ·
   task version {{ task_hash }}</div></div>
  <div class="nav">{{ nav }}</div>
</div>

<div class="tiles">
{% for t in tiles %}<div class="tile"><div class="v">{{ t.v }}{% if t.sub %}<span class="vsub" title="{{ t.sub_tip }}">{{ t.sub }}</span>{% endif %}</div><div class="k">{{ t.k }}</div></div>
{% endfor %}</div>

{% if prompt %}
<details class="det"><summary>show the prompt every model received</summary>
<div class="inner"><pre>{{ prompt }}</pre></div></details>
{% endif %}

<h2>Model comparison — every run per model, aggregated · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th class="num">#</th><th data-type="text">Model</th><th data-type="num">Score</th>
<th data-type="text" title="the deciphered reason a non-passing result went the way it did (assess.classify) — attribution + category, full detail on hover">Why</th>
<th class="num" data-type="num">Wall</th>
<th class="num" data-type="num">TTFT</th><th class="num" data-type="num">Tok in</th><th class="num" data-type="num">Tok out</th>
<th></th><th class="num" data-type="num">Tok/s</th><th class="num" data-type="num">Cost</th>
<th class="num" data-type="num">Retries</th><th data-type="text">Run</th>
{% if files_col %}<th title="browse this model's files for this exact run — workspace (the app it built), transcript, metrics, score">Files</th>{% endif %}</tr>
{% for r in rows %}
<tr id="row-{{ r.slug }}"><td class="num">{{ loop.index }}</td><td class="model">{{ r.model_link }}</td>
<td class="num nowrap">{{ r.chip }}{{ r.fail }}{% if r.sigma %}<span class="sig" title="mean of {{ r.n_scored }} scored run(s) · σ {{ r.sigma }}">{{ r.sigma }}</span>{% endif %}</td><td class="small nowrap">{{ r.why }}</td>
<td class="num">{{ r.wall }}</td><td class="num">{{ r.ttft }}</td>
<td class="num">{{ r.tin }}</td><td class="num">{{ r.tout }}</td><td>{{ r.tout_bar }}</td>
<td class="num">{{ r.tps }}</td><td class="num">{{ r.cost }}</td>
<td class="num">{{ r.retries }}</td>
<td class="small nowrap"><a href="../runs/{{ r.run_id }}.html">{{ r.run_id }}</a>{% if r.nrun_badge %} <span class="nrun" title="{{ r.nrun_title }}">{{ r.nrun_badge }}</span>{% endif %}</td>
{% if files_col %}<td class="small nowrap"><a class="filelink" href="{{ r.files }}"{% if r.n_runs > 1 %} title="{{ r.nrun_title }}"{% endif %}>files ↗</a></td>{% endif %}</tr>
{% endfor %}</table></div>

<h2>What each model actually produced</h2>
{% for r in rows %}
<details class="det" id="m-{{ r.slug }}"><summary><b>{{ r.model }}</b> — {{ r.chip }}{{ r.fail }} · {{ r.summary }}{% if r.why_full %} · <i>{{ r.why_full }}</i>{% endif %}</summary>
<div class="inner"><pre>{{ r.output }}</pre></div></details>
{% endfor %}
{{ focus_js }}

{% if history|length > rows|length %}
<h2>Full history</h2>
<div class="card"><table>
<tr><th>Run</th><th>Model</th><th>Score</th><th class="num">Wall</th>
<th class="num">Tok in / out</th><th class="num">Cost</th></tr>
{% for h in history %}
<tr><td class="small"><a href="../runs/{{ h.run_id }}.html">{{ h.run_id }}</a></td>
<td class="model">{{ h.model }}</td><td>{{ h.chip }}</td>
<td class="num">{{ h.wall }}</td><td class="num">{{ h.tokens }}</td>
<td class="num">{{ h.cost }}</td></tr>
{% endfor %}</table></div>
{% endif %}

<div class="foot">Latest-per-model table ranks by score, then cost, then speed.
Token counts come from provider usage fields. Outputs are verbatim transcripts,
truncated for display — full text lives in runs/…/transcript.jsonl.</div>
{{ sort_js }}
</body></html>"""

INDEX_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Testing · Overview</title>
<link rel="alternate" type="application/atom+xml" title="LLM Testing — models tested" href="feed.xml">
<style>{{ css }}
/* .seg (segmented toggle) now lives in BASE_CSS — shared with /discriminate */
/* ---- matrix-first overview hero (tokens live in BASE_CSS) ---- */
.mast { border-bottom:2px solid var(--ink); padding-bottom:16px; margin:18px 0 4px; }
.mast .eyebrow { font-family:var(--mono); font-size:11px; letter-spacing:.2em;
  text-transform:uppercase; color:var(--muted); display:flex; gap:6px 14px; flex-wrap:wrap; }
.statline { display:flex; flex-wrap:wrap; align-items:flex-end; margin-top:16px; row-gap:14px; }
.statline .stat { padding:0 22px; border-left:1px solid var(--hair); }
.statline .stat:first-child { padding-left:0; border-left:none; }
.stat .n { font-size:29px; font-weight:750; letter-spacing:-.02em; line-height:1;
  font-variant-numeric:tabular-nums; }
.stat .n small { font-size:14px; color:var(--ink-2); font-weight:500; margin-left:2px; }
.stat .n.up { color:var(--accent); }
.stat .n.warn { color:var(--warn); }
.stat .k { font-family:var(--mono); font-size:10px; letter-spacing:.11em; text-transform:uppercase;
  color:var(--muted); margin-top:7px; }
.stat .d { font-size:11.5px; color:var(--ink-2); margin-top:2px; }
/* .mx-* / .mxlegend matrix styles now live in BASE_CSS (shared with the model page) */
</style></head><body>
<div class="topbar">
  <div><h1>LLM Testing</h1>
  <div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}one
  suite version per dataset · suite v{{ suite_version }}{% if data_asof %} ·
  <strong>data as of {{ data_asof }}</strong> · <a href="feed.xml">feed</a>{% endif %}</div></div>
  <div class="nav"><select id="dsnav" title="switch dataset version"
    style="background:var(--surface);color:var(--ink);border:1px solid var(--border);
    border-radius:7px;padding:4px 8px;font:inherit;font-size:12.5px"></select>
  {{ nav }}</div>
</div>
{% if dataset_caveat %}
<div class="card" style="border-left:3px solid var(--warn,#c90);background:var(--surface);
  margin:10px 0;padding:10px 14px;font-size:13px">⚠ {{ dataset_caveat }}</div>
{% endif %}
<script>
(async () => {
  const sel = document.getElementById('dsnav');
  try {
    const v = await (await fetch('/api/versions')).json();
    const cur = "{{ dataset_key }}";
    sel.innerHTML = `<option value="live">live — v${v.live}</option>` +
      v.archives.slice().reverse().map(a =>
        `<option value="${a.key}">archived v${a.key} (${a.runs} runs)</option>`).join('');
    sel.value = cur || 'live';
    sel.addEventListener('change', () => {
      location.href = sel.value === 'live' ? '/' :
        `/datasets/v${sel.value}/index.html`;
    });
  } catch (e) { sel.style.display = 'none'; }  // static file:// viewing
})();
</script>

<div class="mast">
  <div class="eyebrow">{% for e in mast_eyebrow %}<span>{{ e }}</span>{% endfor %}</div>
  <div class="statline">
  {% for s in mast_stats %}<div class="stat"><div class="n{% if s.up %} up{% endif %}{% if s.warn %} warn{% endif %}">{{ s.n }}</div><div class="k">{{ s.k }}</div>{% if s.d %}<div class="d">{{ s.d }}</div>{% endif %}</div>
  {% endfor %}</div>
</div>

{% if matrix %}
<h2>Every model, every task <span class="small muted" style="text-transform:none;letter-spacing:0;font-weight:400">· rows ranked by mean · ± is the 95% band across tasks · <span class="tie" style="color:var(--accent);font-weight:700">≈</span> marks models tied with the leader within noise · hover a cell for the task · <a href="info.html#fail">what the colours mean →</a></span></h2>
<div class="seg" id="mxseg" title="narrow the grid to one end of the suite — rows re-rank by that subset's mean">
  <button type="button" data-mx="all" class="on">All ({{ matrix.n_all }})</button>
  <button type="button" data-mx="hard">◆ Hard ({{ matrix.n_hard }})</button>
  <button type="button" data-mx="easy">Easy ({{ matrix.n_easy }})</button>
</div>
<div class="mx-scroll"><div class="mx">
  <div class="mx-row head">
    <div class="mx-rail"><span class="rk"></span><span class="nm">Model</span><span class="sc">Score</span><span class="gp">Gap</span></div>
    <div class="mx-cells">{% for c in matrix.cats %}<div class="mx-grp" style="grid-template-columns:repeat({{ c.n }},15px);gap:3px"><span class="mx-clabel" title="{{ c.key }}" style="grid-column:1/-1">{{ c.code }} <span class="cn">{{ c.n }}</span></span></div>{% endfor %}</div>
  </div>
  {% for r in matrix.rows %}
  <div class="mx-row{% if r.lead %} lead{% endif %}" data-all="{{ r.m_all }}" data-hard="{{ r.m_hard }}" data-easy="{{ r.m_easy }}">
    <div class="mx-rail"><span class="rk">{{ r.rank }}</span><span class="nm">{{ r.model }}</span><span class="sc">{{ r.score }}{% if r.ci %}<span class="ci" title="95% confidence band across tasks (±1.96·SE)">{{ r.ci }}</span>{% endif %}</span><span class="gp">{% if r.tied %}<span class="tie" title="within the leader's 95% band — not statistically distinguishable on this task set">≈</span>{% endif %}{{ r.gap }}</span></div>
    <div class="mx-cells">{% for g in r.groups %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}" data-sub="{{ cell.sub }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
  {% endfor %}
  <div class="mx-row foot">
    <div class="mx-rail"><span class="fl">fleet avg / task →</span></div>
    <div class="mx-cells">{% for g in matrix.foot %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}" data-sub="{{ cell.sub }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
</div></div>
<script>
(function(){
  var seg=document.getElementById('mxseg'), mx=document.querySelector('.mx');
  if(!seg||!mx) return;
  var rows=[].slice.call(mx.querySelectorAll('.mx-row:not(.head):not(.foot)'));
  var head=mx.querySelector('.mx-row.head'), foot=mx.querySelector('.mx-row.foot');
  function vis(g){ return [].slice.call(g.querySelectorAll('.mx-cell')).filter(function(c){ return c.style.display!=='none'; }).length; }
  function apply(sub){
    rows.concat(foot?[foot]:[]).forEach(function(r){
      [].slice.call(r.querySelectorAll('.mx-cell')).forEach(function(c){
        c.style.display=(sub==='all'||c.dataset.sub===sub)?'':'none';
      });
      [].slice.call(r.querySelectorAll('.mx-grp')).forEach(function(g){
        g.style.display=vis(g)?'':'none';
      });
    });
    if(head&&rows.length){
      var src=[].slice.call(rows[0].querySelectorAll('.mx-grp'));
      [].slice.call(head.querySelectorAll('.mx-grp')).forEach(function(hg,i){
        var n=src[i]?vis(src[i]):0;
        hg.style.display=n?'':'none';
        hg.style.gridTemplateColumns='repeat('+n+',15px)';
        var cn=hg.querySelector('.cn'); if(cn) cn.textContent=n;
      });
    }
    var scored=rows.map(function(r){ return {r:r, v:parseFloat(r.dataset[sub])}; });
    scored.sort(function(a,b){ return (isNaN(b.v)?-1:b.v)-(isNaN(a.v)?-1:a.v); });
    var lead=scored.length?scored[0].v:NaN, parent=rows.length?rows[0].parentNode:null;
    scored.forEach(function(o,i){
      if(parent&&foot) parent.insertBefore(o.r,foot);
      var sc=o.r.querySelector('.sc'), rk=o.r.querySelector('.rk'), gp=o.r.querySelector('.gp');
      if(sc) sc.textContent=isNaN(o.v)?'—':o.v.toFixed(3);
      if(rk) rk.textContent=i+1;
      if(gp) gp.textContent=(i===0||isNaN(o.v)||isNaN(lead))?'—':'+'+(lead-o.v).toFixed(3).replace(/^0/,'');
      o.r.classList.toggle('lead', i===0&&!isNaN(o.v));
    });
  }
  [].slice.call(seg.querySelectorAll('button')).forEach(function(b){
    b.addEventListener('click',function(){
      [].slice.call(seg.querySelectorAll('button')).forEach(function(x){ x.classList.toggle('on',x===b); });
      apply(b.dataset.mx);
    });
  });
})();
</script>
<div class="mxlegend">
  <div class="grp"><span class="k">Score</span><span class="ramp"><i style="--a:.15"></i><i style="--a:.4"></i><i style="--a:.65"></i><i style="--a:.9"></i><i style="--a:1"></i></span><span class="k" style="letter-spacing:0">0 → 1.0</span></div>
  <div class="grp"><span class="sw" style="background:var(--trap)"></span><span class="k">fell-for-trap</span></div>
  <div class="grp"><span class="sw" style="background:var(--miss)"></span><span class="k">retrieval-miss</span></div>
  <div class="grp"><span class="sw" style="background:var(--crit)"></span><span class="k">gave up / DNF</span></div>
  <div class="grp"><span class="sw na"></span><span class="k">n/a · excluded</span></div>
</div>
<div class="mxlegend" style="margin-top:8px">
  {% for c in matrix.cats %}<div class="grp"><span class="k" style="color:var(--ink-2)">{{ c.code }}</span><span class="k" style="letter-spacing:0;text-transform:none">{{ c.key }}</span></div>{% endfor %}
</div>
{% endif %}

{% if podium %}
<h2>Leaderboard — each model's aggregated result per task · tries/pass = attempts ÷ perfect passes (lower is better) · click a model for its history</h2>
<p class="small muted" style="margin:-6px 0 12px">A model that hasn't attempted
the whole suite is <strong>not ranked</strong>: its mean isn't comparable, and the
tasks it's missing skew toward the ones it failed or never reached. Those models
are shown last, marked <span class="pill" style="border-color:var(--warn);color:var(--warn)">partial</span>.</p>
<div class="podium">
{% for p in podium %}
<a class="pcard m{{ loop.index if (loop.index <= 3 and not p.partial) else 0 }}" href="models/{{ p.slug }}.html">
  <span class="cardarrow">→</span>
  <div class="rank">{% if p.partial %}<span style="color:var(--warn)">unranked</span>{% else %}{% if loop.index == 1 %}★ {% endif %}#{{ loop.index }}{% endif %}</div>
  <div class="name">{{ p.model }}</div>
  {% if p.model_id and p.model_id != p.model %}<div class="small muted" style="margin:-2px 0 4px;font-size:11px">{{ p.model_id }}</div>{% endif %}
  <div class="score">{{ p.score }}<small> / 1.000</small>{% if p.ci %}<span class="pci" title="95% confidence band across tasks (±1.96·SE)">{{ p.ci }}</span>{% endif %}</div>
  <div class="subs">
  {% if p.partial %}<b style="color:var(--warn)">partial — {{ p.coverage }} tasks</b><br>{% else %}<span class="muted">{{ p.coverage }} tasks</span><br>{% endif %}
  <b>{{ p.app }}</b> tries/pass
  <span class="muted">· {{ p.app_ctx }}</span><br>
  <b>{{ p.tps }}</b> tok/s · <b>{{ p.cost }}</b>/run · {{ p.where }}<br>
  <b>{{ p.total_time }}</b> total time</div>
</a>
{% endfor %}</div>

<h2 style="margin-bottom:2px">Standings — rank by a lens, filter by where it runs</h2>
<div class="seg" data-seg="rank" title="restacks the table and renumbers # by the chosen lens">
  <button class="on" data-f="pure">Pure</button>
  <button data-f="value">Value</button>
  <button data-f="speed">Speed</button>
  <button data-f="eff">Efficiency</button>
  <button data-f="hard">Hard tasks</button>
  <button data-f="easy">Easy tasks</button>
  <button data-f="firsttry">First-try</button>
</div>
<div class="seg" data-seg="standings">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local ⚡</button>
  <button data-f="remote">API / CLI</button>
</div>
<div id="rankwhat" class="foot" style="margin:0 0 8px"></div>
<div id="gpufit" style="display:none;margin:2px 0 10px;font-size:12.5px;color:var(--ink-dim)">
  Fits my GPU:
  <select id="gpugb"><option value="0">any size</option><option>8</option>
  <option>12</option><option>16</option><option>24</option><option>32</option>
  <option>48</option><option>80</option></select> GB VRAM, at
  <select id="gpuctx"><option value="4096">4k</option><option value="8192">8k</option>
  <option value="16384" selected>16k</option><option value="32768">32k</option>
  <option value="65536">64k</option><option value="131072">128k</option></select>
  context · <label><input type="checkbox" id="gpuhide"> hide models that don't fit</label>
</div>
<div class="card"><table class="sortable" id="standings">
<tr><th data-type="num">#</th><th data-type="text">Model</th>
<th class="num lenscol" data-type="num" id="lenshdr" title="the metric the active Rank-by lens sorts on — changes with the lens above"><span id="lenslabel">Score</span></th>
<th data-type="text">Where</th><th data-type="num">Score</th>
<th class="num" data-type="num" title="the model's WORST single-task score — a mean near 1.0 can still hide one bad task; hover a cell for which task">Low</th>
<th data-type="num">Coverage</th><th data-type="num">tok/s</th>
<th data-type="num" title="an estimate, not a bill"><a href="info.html#pricing">Cost/run</a></th>
<th class="num" data-type="num" title="score per dollar; a local model's dollar is measured GPU electricity ⚡">Score / $</th>
<th data-type="num" title="weights on disk + quant; picking a GPU size shows VRAM needed at your context">VRAM / fit</th></tr>
{% for r in standings %}
<tr data-kind="{{ r.kind }}" data-w="{{ r.w_v }}" data-kvtok="{{ r.kvtok }}"
    data-kvfixed="{{ r.kvfixed }}" data-native="{{ r.native }}"
    data-pure="{{ r.pure_v }}" data-value="{{ r.value_v }}" data-speed="{{ r.speed_v }}"
    data-eff="{{ r.eff_v }}" data-hard="{{ r.hard_v }}" data-easy="{{ r.easy_v }}" data-firsttry="{{ r.firsttry_v }}">
<td class="num">{{ r.rank }}</td>
<td class="nowrap">{{ r.model }}</td>
<td class="num lensval" data-sort="{{ r.score_v }}">{{ r.score }}</td>
<td class="small">{{ r.where }}</td>
<td class="num" data-sort="{{ r.score_v }}">{{ r.score }}</td>
<td class="num" data-sort="{{ r.low_v }}" title="worst task: {{ r.low_task }}">{{ r.low }}</td>
<td class="num">{{ r.cov }}</td>
<td class="num" data-sort="{{ r.tps_v }}">{{ r.tps }}</td>
<td class="num">{{ r.cost }}</td>
<td class="num">{{ r.value }}</td>
<td class="small fitcell num" data-size="{{ r.size_disp }}">{{ r.size_disp }}</td></tr>
{% endfor %}</table></div>
<div class="foot" style="margin-top:6px">Local and API/CLI models are different
constraint classes — a combined mean isn't comparable, so filter to yours.
<b>Score / $</b> is quality per dollar; for a local model that dollar is
<b>measured GPU electricity</b> (⚡), not an API bill. <b>VRAM / fit</b> is the
model's weights on disk; pick a GPU size under <b>Local</b> to see the VRAM it
needs at your context (weights + KV cache) and whether it fits — measured from
the GGUF, not the run's loaded window.</div>
{% endif %}

{% if bump %}
<h2>Rankings across suite versions</h2>
<div class="card chartcard">{{ bump }}</div>
<div class="foot" style="margin-top:6px">Each column is one dataset version
(archived or live); lines trace a model's leaderboard <b>rank</b>. Ranks are
the honest cross-version comparison — raw scores are not comparable because
the tests change between versions. Solid lines: models tested in every
version; dashed/faded: partial coverage. Ties share a rank.
<b>Datasets before v0.5</b> predate the no-op-floor fixes (v0.5.5–0.5.6) and
timing calibration (v0.5.9), so their ranks can over-credit weak models on
agentic/timing tasks — read the earliest columns with that caveat.</div>
{% endif %}

<h2>Value — is a model worth its cost / speed? · hover for every model under the cursor</h2>
<div class="chartkey"><span class="k-dot"></span> a model &nbsp;
  <span class="k-dot dim"></span> dominated (something cheaper/faster scores at
  least as high) &nbsp; <span class="k-line"></span> Pareto frontier</div>
{% if cost_scatter %}
<div class="foot" style="margin:0 0 4px">Score vs <b>cost to run the full
  suite</b> — API / CLI models (a local model's "cost" is just electricity)</div>
<div class="card chartcard">{{ cost_scatter }}</div>
{% endif %}
<div class="foot" style="margin:14px 0 4px">Score vs <b>generation speed</b></div>
<div class="seg" data-seg="valspeed">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local ⚡</button>
  <button data-f="remote">API / CLI</button>
</div>
{% for key in ['all','local','remote'] %}
<div data-vcohort="{{ key }}"{% if key != 'all' %} style="display:none"{% endif %}>
<div class="card chartcard">{{ speed_scatter[key] }}</div></div>
{% endfor %}

<h2>Score by category — aggregated result per task · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Model</th>{% for c in categories %}<th data-type="num">{{ c }}</th>{% endfor %}</tr>
{% for row in cat_rows %}
<tr><td data-sort="{{ row.model_sort }}">{{ row.model }}</td>
{% for c in row.cells %}<td class="num" data-sort="{{ c.sort }}">{{ c.html }}</td>{% endfor %}</tr>
{% endfor %}</table></div>

<h2 style="margin-bottom:2px">Task fit — which model for which job <a href="info.html#fit" class="small" style="font-weight:400">how this is decided →</a></h2>
<div class="seg" data-seg="fit">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local only ⚡</button>
  <button data-f="remote">API / CLI only</button>
</div>
{% for key, rows in [('all', fit_rows), ('local', fit_local), ('remote', fit_remote)] %}
<div data-cohort="{{ key }}"{% if key != 'all' %} style="display:none"{% endif %}>
<div class="card"><table>
<tr><th>Category</th>
<th title="how many models clear the capable bar — the shape of the lane">Capable</th>
<th title="best score; when the field ties, the tie count is what matters, not the name">Best</th>
<th title="cheapest DURABLE cost that still clears the bar (local electricity or a genuinely paid API). Promotional :free variants are listed under it separately — their $0 expires.">Cheapest that works</th>
<th title="fastest model that still clears the bar">Fastest that works</th>
<th>Below par</th></tr>
{% for f in rows %}
<tr><td class="model">{{ f.category }}</td>
<td class="num small"><b>{{ f.n_ok }}</b><span class="muted">/{{ f.n_total }}</span></td>
<td class="small nowrap">{{ f.best }}</td>
<td class="small nowrap">{{ f.cheap }}{% if f.freebie %}<div class="muted" style="font-size:11px">free now: {{ f.freebie }}</div>{% endif %}</td>
<td class="small nowrap">{{ f.fast }}</td>
<td class="small muted">{% if f.n_bad %}<b>{{ f.n_bad }}</b> · {{ f.avoid }}{% if f.avoid_all %}
  <a href="#" class="fitmore" data-more="{{ loop.index0 }}-{{ key }}">…{{ f.n_bad - 3 }} more</a>
  <span id="more-{{ loop.index0 }}-{{ key }}" style="display:none">, {{ f.avoid_all }}</span>{% endif %}{% else %}—{% endif %}</td></tr>
{% endfor %}</table></div></div>
{% endfor %}
<script>
document.querySelectorAll('.fitmore').forEach(function(a){
  a.addEventListener('click', function(e){
    e.preventDefault();
    var s=document.getElementById('more-'+a.dataset.more);
    if(s){ s.style.display=''; a.style.display='none'; }
  });
});
</script>
<div class="foot" style="margin-top:6px"><b>Capable</b> is how many of the fleet
clear the bar — when it reads 35/35 the lane is saturated and a score ranking is
meaningless (they all tie), so the real answer is the <b>cheapest that works</b>:
you do not need a frontier model for that job. When Capable is low, the lane
genuinely separates and <b>Best</b> is the answer.
<b>Cheapest counts only durable costs</b> — a local model's measured electricity,
or a genuinely paid API. OpenRouter's promotional <code>:free</code> variants are
listed beneath it as “free now” and marked ⏳: their $0 is a true record of what
that run was billed, but it is a promotion, not a price you can plan on
(<a href="info.html#freetier">why this matters →</a>). Filter
to the models you can actually run. {{ fit_note }} Thresholds live in
<code>directives.yaml</code> (excellent ≥ {{ fit_th.excellent }}, capable ≥
{{ fit_th.capable }}, value pick ≥ {{ fit_vp.min_tps }} tok/s) — edit and the
classification updates on the next report regeneration.</div>

<h2>Value &amp; consistency — aggregated result per task · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Model</th><th class="num" data-type="num">First-try clean</th>
<th class="num" data-type="num" title="attempts ÷ perfect passes — lower is better">Tries / pass</th>
<th class="num" data-type="num">Score / min</th>
<th class="num" data-type="num">Score / $</th><th class="num" data-type="num">p50 task</th><th class="num" data-type="num">p95 task</th>
<th class="num" data-type="num" title="mean per-task σ: when the SAME task is run again, how far the score moves. '—' until something has been run twice.">σ per task</th>
<th data-type="text" title="the single task whose score moved most between repeat runs — where this model is least reproducible">Least stable</th></tr>
{% for row in value_rows %}
<tr><td class="nowrap">{{ row.model }}</td><td class="num">{{ row.first_try }}</td>
<td class="num">{{ row.app }}</td>
<td class="num">{{ row.spm }}</td><td class="num">{{ row.spd }}</td>
<td class="num">{{ row.p50 }}</td><td class="num">{{ row.p95 }}</td>
<td class="num nowrap" data-sort="{{ row.sigma_sort }}" title="{{ row.sigma_title }}">{{ row.sigma }}<span class="snote">{{ row.sigma_note }}</span></td>
<td class="small nowrap">{{ row.worst }}</td></tr>
{% endfor %}</table></div>

<h2>Speed &amp; cost — aggregated result per task · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Model</th><th class="num" data-type="num">Gen tok/s</th><th></th>
<th class="num" data-type="num">Prefill tok/s</th><th class="num" data-type="num">TTFT</th>
<th class="num" data-type="num">Tokens</th><th class="num" data-type="num"><a href="info.html#pricing">Cost / run</a></th><th class="num" data-type="num">Cold start</th>
<th class="num" data-type="num">Peak VRAM</th><th class="num" data-type="num">Avg power</th><th class="num" data-type="num">Energy</th>
<th class="num" data-type="num" title="GPU energy x your electricity rate (directives.yaml). Marginal and GPU-only: excludes CPU/system draw and hardware amortisation."><a href="info.html#pricing">Power cost</a></th>
<th data-type="text">Where</th></tr>
{% for row in speed_rows %}
<tr><td class="nowrap">{{ row.model }}</td><td class="num">{{ row.tps }}</td>
<td>{{ row.tps_bar }}</td><td class="num">{{ row.prefill }}</td>
<td class="num">{{ row.ttft }}</td>
<td class="num nowrap">{{ row.tokens }}</td><td class="num nowrap">{{ row.cost }}</td>
<td class="num nowrap">{{ row.cold }}</td>
<td class="num nowrap">{{ row.vram }}</td><td class="num nowrap">{{ row.watts }}</td>
<td class="num nowrap">{{ row.energy }}</td>
<td class="num nowrap">{{ row.energy_cost }}</td>
<td class="small nowrap">{{ row.where }}</td></tr>
{% endfor %}</table></div>

{% if frontier %}
<h2>Efficiency frontier — quality vs verbosity</h2>
<div class="card chartcard"><div class="chartwrap">
<div class="chartsvg">{{ frontier }}</div>{{ legend_html }}</div></div>
{% endif %}

<h2>Tasks — click a task for the cross-model comparison · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Task</th><th data-type="text">Title</th>
<th data-type="text">Category</th><th class="num" data-type="num">Tier</th>
<th data-type="text">Scoring</th><th class="num" data-type="num">Models tested</th>
<th class="num" data-type="num" title="models that scored a perfect 1.0, out of tested — high = saturated (retire or harden it), low = discriminating">Aced</th>
<th class="num" data-type="num" title="max − min score across models — 0.00 = everyone landed the same, high = the task separates the field">Spread</th>
<th data-type="text" title="◆ = in the curated hardened suite (config.HARDENED_TASKS), the set chosen for 3× repeat runs. Distinct from the live frontier/discriminator flags on the Discriminate page.">3×</th></tr>
{% for t in task_rows %}
<tr><td class="nowrap"><a href="tasks/{{ t.id }}.html">{{ t.id }}</a></td>
<td class="small">{{ t.title }}</td><td class="small">{{ t.category }}</td>
<td class="num">{{ t.tier }}</td><td class="small">{{ t.scoring }}</td>
<td class="num">{{ t.n_models }}</td>
<td class="num" data-sort="{{ t.aced_frac }}">{{ t.aced }}</td>
<td class="num" data-sort="{{ t.spread_v }}">{{ t.spread }}</td>
<td data-sort="{{ '1' if t.hardened else '0' }}">{% if t.hardened %}<span class="hardmark" title="hardened suite — 3× repeat set">◆</span>{% endif %}</td></tr>
{% endfor %}</table></div>

<h2>Runs</h2>
<div class="card"><table>
<tr><th>Run</th><th>Suite</th><th>Tag</th><th>Models</th><th class="num">Tasks</th>
<th>Raw data</th><th></th></tr>
{% for r in runs %}
<tr><td><a href="runs/{{ r.run_id }}.html">{{ r.run_id }}</a></td>
<td class="small">v{{ r.manifest.suite_version or "?" }}</td>
<td class="small">{{ r.manifest.tag }}</td>
<td class="small">{{ r.manifest.models|join(", ") }}</td>
<td class="num">{{ r.manifest.tasks|length }}</td>
<td class="small"><a href="/data/{{ r.run_id }}/">browse →</a></td>
<td><button class="delrun" data-run="{{ r.run_id }}"
  title="delete this run's data permanently">✕</button></td></tr>
{% endfor %}</table></div>
<script>
document.querySelectorAll('.delrun').forEach(b => b.addEventListener('click', async () => {
  if (!confirm('Permanently delete run ' + b.dataset.run +
      ' and all its transcripts/results?')) return;
  const r = await fetch('/api/delete-run', {method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({run: b.dataset.run})});
  if (r.ok) location.reload();
  else alert('delete failed: ' + await r.text());
}));

// chart ↔ legend cross-highlight: hovering a legend entry (or a dot) dims
// every other model so a single series is traceable without connecting lines
document.querySelectorAll('.chartwrap').forEach(wrap => {
  const svg = wrap.querySelector('svg');
  const legend = wrap.querySelector('.clegend');
  if (!svg) return;
  const focus = (slug) => {
    wrap.classList.toggle('focus', !!slug);
    if (legend) legend.classList.toggle('focus', !!slug);
    svg.querySelectorAll('.dot').forEach(d =>
      d.classList.toggle('on', d.dataset.m === slug));
    if (legend) legend.querySelectorAll('.cl-item').forEach(i =>
      i.classList.toggle('on', i.dataset.m === slug));
  };
  if (legend) legend.querySelectorAll('.cl-item').forEach(item => {
    item.addEventListener('mouseenter', () => focus(item.dataset.m));
    item.addEventListener('mouseleave', () => focus(null));
  });
  svg.querySelectorAll('.dot').forEach(d => {
    d.addEventListener('mouseenter', () => focus(d.dataset.m));
    d.addEventListener('mouseleave', () => focus(null));
  });
});

// rankings bump chart: hover a bubble (or a name) to highlight every model
// sharing that rank — including overlapping tied bubbles
(() => {
  const svg = document.querySelector('svg.bump');
  if (!svg) return;
  const groups = [...svg.querySelectorAll('.bm')];
  const light = (slugs) => {
    svg.classList.toggle('focus', !!slugs);
    groups.forEach(g => g.classList.toggle('on',
      !!slugs && slugs.indexOf(g.dataset.m) !== -1));
  };
  // node hit targets carry the list of all models tied at that position
  svg.querySelectorAll('.bmhit').forEach(h => {
    const ms = h.dataset.ms.split(',');
    h.addEventListener('mouseenter', () => light(ms));
    h.addEventListener('mouseleave', () => light(null));
  });
  // hovering a model's name highlights just that model's whole trajectory
  groups.forEach(g => {
    const label = g.querySelector('.bmlabel');
    if (!label) return;
    label.addEventListener('mouseenter', () => light([g.dataset.m]));
    label.addEventListener('mouseleave', () => light(null));
  });
})();
</script>

<div class="foot">Token counts come from each provider's usage field and are only
comparable within a model family (tokenizers differ) — tok/s and cost are the
fair cross-model axes. Gen tok/s excludes time-to-first-token. Wall times include
every retry. Cost for subscription models (claude-cli) shows the API-equivalent
price. A ✓ after a cost means it is the gateway's actual billed amount
(OpenRouter usage accounting) rather than yaml list pricing; "via &lt;host&gt;"
names the upstream provider that actually served the requests.{% if not public_nav %}
Chart colors and overview visibility are per-model settings on the
<a href="/run">Run</a> page.{% endif %}</div>
<script>
// segmented controls: standings filters by where-it-runs (+ a GPU-fit gate
// when Local is active); fit swaps the recomputed cohort tables.
function applyStandings() {
  const seg = document.querySelector('.seg[data-seg="standings"]');
  const f = (seg.querySelector('button.on') || {}).dataset ?
            seg.querySelector('button.on').dataset.f : 'all';
  const gating = (f === 'local');
  const box = document.getElementById('gpufit');
  if (box) box.style.display = gating ? '' : 'none';
  const gpu = +((document.getElementById('gpugb') || {}).value || 0);
  const ctx = +((document.getElementById('gpuctx') || {}).value || 0);
  const hide = (document.getElementById('gpuhide') || {}).checked;
  document.querySelectorAll('#standings tr[data-kind]').forEach(tr => {
    let show = (f === 'all' || tr.dataset.kind === f);
    const cell = tr.querySelector('.fitcell');
    const w = +tr.dataset.w;
    if (gating && w > 0 && cell) {
      const need = w + (+tr.dataset.kvfixed) + (+tr.dataset.kvtok) * ctx;
      const native = +tr.dataset.native;
      const fits = gpu === 0 || (need <= gpu && (native === 0 || ctx <= native));
      if (gpu === 0) { cell.textContent = cell.dataset.size; cell.style.color = ''; }
      else {
        cell.textContent = (fits ? '✓ ' : '✗ ') + need.toFixed(1) + ' GB';
        cell.style.color = fits ? 'var(--good, #3a3)' : 'var(--bad, #c55)';
      }
      if (hide && !fits) show = false;
    } else if (cell) { cell.textContent = cell.dataset.size; cell.style.color = ''; }
    tr.style.display = show ? '' : 'none';
  });
  applyRank();
}
const RANK_WHAT = {
  pure: 'Ranked by raw suite score.',
  value: 'Ranked by score per dollar — a local model\\'s dollar is measured GPU electricity, so filter to one class to compare like-for-like.',
  speed: 'Ranked by score per minute — quality per unit of wall-clock time to reach it (not raw tok/s).',
  eff: 'Ranked Pareto-efficient first: a model not beaten on score AND cost AND speed leads; dominated ones sink below the line.',
  hard: 'Ranked by score on the discriminating hard-task subset — cuts through the top-end saturation where everyone scores ~0.99.',
  easy: 'Ranked by score on the easy subset — the tasks almost every model gets right. The order here is SUPPOSED to be flat: if a model drops on this lens it is failing the everyday work, not the frontier.',
  firsttry: 'Ranked by first-try-clean rate: the share of tasks nailed at 1.0 with zero retries.'
};
// each lens: the column HEADER label + how to render its value, derived from
// the same data-* number the sort uses — so the "Ranked by" column always shows
// the metric the order is based on (no more sorting on an invisible number).
const LENS_META = {
  pure:    {label:'Score',       fmt:v=>v.toFixed(3)},
  value:   {label:'Score / $',   fmt:v=>v.toLocaleString(undefined,{maximumFractionDigits:1})},
  speed:   {label:'Score / min', fmt:v=>v.toFixed(2)},
  eff:     {label:'Efficiency',  fmt:v=>v>=10?'frontier':'dominated'},
  hard:    {label:'Hard score',  fmt:v=>v.toFixed(3)},
  easy:    {label:'Easy score',  fmt:v=>v.toFixed(3)},
  firsttry:{label:'First-try',   fmt:v=>(v*100).toFixed(0)+'%'}
};
function activeLens(){
  const seg = document.querySelector('.seg[data-seg="rank"]');
  const b = seg && seg.querySelector('button.on');
  return b ? b.dataset.f : 'pure';
}
function applyRank(){
  const lens = activeLens();
  const meta = LENS_META[lens] || LENS_META.pure;
  const what = document.getElementById('rankwhat');
  if (what) what.textContent = RANK_WHAT[lens] || '';
  const lbl = document.getElementById('lenslabel');
  if (lbl) lbl.textContent = meta.label;
  const rows = [].slice.call(document.querySelectorAll('#standings tr[data-kind]'));
  if (!rows.length) return;
  const val = tr => { const v = parseFloat(tr.dataset[lens]); return isNaN(v) ? -Infinity : v; };
  // fill the dynamic "Ranked by" cell for each row with THIS lens's value
  rows.forEach(tr => { const cell = tr.querySelector('.lensval'); if (!cell) return;
    const raw = tr.dataset[lens]; const v = parseFloat(raw);
    cell.textContent = (raw === '' || isNaN(v)) ? '—' : meta.fmt(v);
    cell.setAttribute('data-sort', isNaN(v) ? '' : v);
  });
  rows.sort((a, b) => val(b) - val(a));           // descending; blanks last
  const parent = rows[0].parentNode;
  rows.forEach(tr => parent.appendChild(tr));      // restack the DOM
  let n = 0;                                        // renumber the VISIBLE rows
  rows.forEach(tr => { if (tr.style.display !== 'none') tr.querySelector('td').textContent = ++n; });
}
document.querySelectorAll('.seg').forEach(seg => {
  seg.addEventListener('click', e => {
    const btn = e.target.closest('button'); if (!btn) return;
    seg.querySelectorAll('button').forEach(b => b.classList.toggle('on', b === btn));
    if (seg.dataset.seg === 'standings' || seg.dataset.seg === 'rank') {
      applyStandings();
    } else if (seg.dataset.seg === 'fit') {
      const f = btn.dataset.f;
      document.querySelectorAll('[data-cohort]').forEach(el => {
        el.style.display = (el.dataset.cohort === f) ? '' : 'none';
      });
    } else if (seg.dataset.seg === 'valspeed') {
      const f = btn.dataset.f;
      document.querySelectorAll('[data-vcohort]').forEach(el => {
        el.style.display = (el.dataset.vcohort === f) ? '' : 'none';
      });
    }
  });
});
['gpugb', 'gpuctx', 'gpuhide'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', applyStandings);
});
applyStandings();   // establish the default lens caption + ordering on load
</script>
{{ scatter_js }}
{{ sort_js }}
</body></html>"""

_env = Environment(loader=BaseLoader(), autoescape=False)

_FOCUS_JS = r"""<script>
(function(){
function focus(){
  var h = location.hash || '';
  if (h.indexOf('#m-') !== 0) return;
  var slug = h.slice(3);
  document.querySelectorAll('tr.hit').forEach(function(t){ t.classList.remove('hit'); });
  var row = document.getElementById('row-' + slug);
  if (row) row.classList.add('hit');
  var d = document.getElementById('m-' + slug);
  if (!d) return;
  d.open = true;
  d.classList.add('hit');
  d.scrollIntoView({block:'center'});
}
window.addEventListener('hashchange', focus);
if (document.readyState === 'loading')
  document.addEventListener('DOMContentLoaded', focus);
else focus();
})();
</script>"""

_VERSCMP_JS = r"""<script>
(function(){
  var el = document.getElementById('vc-data');
  if (!el) return;
  var data = JSON.parse(el.textContent);
  var famSel = document.getElementById('vc-fam');
  var aSel = document.getElementById('vc-a'), bSel = document.getElementById('vc-b');
  var out = document.getElementById('vc-out');
  function slug(n){ return (n.replace(/[^a-zA-Z0-9._-]+/g,'-').replace(/^-+|-+$/g,'').toLowerCase()) || 'model'; }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function shade(v){ if (v==null) return ''; var a=(0.10+0.90*Math.max(0,Math.min(1,v))).toFixed(3); return 'background:rgba(var(--cell-rgb),'+a+')'; }
  function box(v){ return '<span class="vc-cell" style="'+shade(v)+'">'+(v==null?'—':v.toFixed(2))+'</span>'; }
  function chip(d){ if (d==null) return '<span class="vc-d flat">—</span>'; var c=d>0.005?'up':(d<-0.005?'down':'flat'); return '<span class="vc-d '+c+'">'+(d>0?'+':'')+d.toFixed(2)+'</span>'; }
  function verd(v){ return '<span class="vc-verd '+v+'">'+(v==='na'?'n/a':v)+'</span>'; }
  function catStrip(cats){ return '<div class="vc-cats">'+cats.map(function(c){ return '<div class="vc-catrow"><span class="vc-cat">'+esc(c.cat)+'</span>'+box(c.a)+'→'+box(c.b)+chip(c.delta)+'<span class="vc-note">'+c.n+' task(s)</span></div>'; }).join('')+'</div>'; }
  function renderModel(d){
    var o=d.overall;
    var h='<div class="vc-sum"><b>'+esc(d.a)+' → '+esc(d.b)+'</b> &nbsp; '+chip(o.delta)+' '+verd(o.verdict)+' <span class="vc-note">on '+o.n+' identical task(s)</span></div>';
    h+=catStrip(d.cats);
    var byc={}; d.tasks.forEach(function(t){ (byc[t.cat]=byc[t.cat]||[]).push(t); });
    h+=Object.keys(byc).sort().map(function(c){
      var rows=byc[c].slice().sort(function(x,y){return x.delta-y.delta;}).map(function(t){
        return '<div class="vc-taskrow">'+box(t.a)+'→'+box(t.b)+chip(t.delta)+'<a href="../tasks/'+esc(t.tid)+'.html">'+esc(t.tid)+'</a>'+(t.tier==='changed'?'<span class="vc-warn" title="the task itself changed between these versions — the delta is not like-for-like">⚠ test changed</span>':'')+'</div>';
      }).join('');
      return '<details class="vc-catdet"><summary>'+esc(c)+'</summary>'+rows+'</details>';
    }).join('');
    var cov=d.coverage;
    if (cov.added.length||cov.retired.length||cov.changed.length)
      h+='<p class="vc-note">not like-for-like: '+cov.added.length+' added in '+esc(d.b)+', '+cov.retired.length+' retired since '+esc(d.a)+', '+cov.changed.length+' test(s) changed (flagged above).</p>';
    return h;
  }
  function renderFamily(d){
    var o=d.overall;
    var h='<div class="vc-sum"><b>'+esc(d.family)+' · '+esc(d.a)+' → '+esc(d.b)+'</b> &nbsp; '+chip(o.delta)+' '+verd(o.verdict)+' <span class="vc-note">'+o.n_members+' member(s) in both · '+o.n_tasks+' identical task-scores</span></div>';
    h+=catStrip(d.cats);
    h+='<div class="vc-members">'+d.members.map(function(m){
      return '<div class="vc-taskrow">'+box(m.a)+'→'+box(m.b)+chip(m.delta)+'<a href="models/'+slug(m.model)+'.html">'+esc(m.model)+'</a></div>';
    }).join('')+'</div>';
    var cov=d.coverage;
    if (cov.added_members.length||cov.dropped_members.length)
      h+='<p class="vc-note">members: '+cov.added_members.length+' new in '+esc(d.b)+' ('+(cov.added_members.map(esc).join(', ')||'—')+'), '+cov.dropped_members.length+' gone since '+esc(d.a)+' ('+(cov.dropped_members.map(esc).join(', ')||'—')+').</p>';
    return h;
  }
  function payload(){ return famSel ? (data[famSel.value]||{versions:[],pairs:{}}) : data; }
  function fill(sel, vals, def){ sel.innerHTML=vals.map(function(v){return '<option>'+esc(v)+'</option>';}).join(''); if (def!=null) sel.value=def; }
  function render(){
    var p=payload();
    var diff=p.pairs[aSel.value+'|'+bSel.value] || p.pairs[bSel.value+'|'+aSel.value];
    if (!diff){ out.innerHTML='<p class="vc-note">pick two different versions this '+(famSel?'family':'model')+' was measured in.</p>'; return; }
    out.innerHTML = famSel ? renderFamily(diff) : renderModel(diff);
  }
  function syncVersions(){
    var vs=(payload().versions)||[];
    fill(aSel, vs, vs[vs.length-2]); fill(bSel, vs, vs[vs.length-1]); render();
  }
  if (famSel){ fill(famSel, Object.keys(data)); famSel.addEventListener('change', syncVersions); }
  aSel.addEventListener('change', render); bSel.addEventListener('change', render);
  syncVersions();
})();
</script>"""

_SORT_JS = r"""<script>
(function(){
function numval(td){
  var ex = td.getAttribute('data-sort');
  if (ex !== null && ex !== ''){ var e = parseFloat(ex); return isNaN(e)?NaN:e; }
  var t = (td.textContent||'').trim();
  if (t==='' || t==='—') return NaN;
  if (/^free$/i.test(t)) return Infinity;
  var m = t.replace(/,/g,'').match(/-?\d*\.?\d+/);
  if (!m) return NaN;
  var v = parseFloat(m[0]);
  if (/\dms\b/.test(t) || /ms$/.test(t)) return v;
  if (/\ds\b/.test(t) || /\ds$/.test(t)) return v*1000;
  if (/\dm\b/.test(t) || /\dm$/.test(t)) return v*60000;
  if (/\dh\b/.test(t) || /\dh$/.test(t)) return v*3600000;
  return v;
}
function textval(td){
  var ex = td.getAttribute('data-sort');
  return ((ex!==null?ex:td.textContent)||'').trim().toLowerCase();
}
document.querySelectorAll('table.sortable').forEach(function(table){
  var headers = [].slice.call(table.rows[0].cells);
  headers.forEach(function(th, col){
    if (!th.dataset.type) return;
    th.insertAdjacentHTML('beforeend', '<span class="caret">▲</span>');
    th.addEventListener('click', function(){
      var num = th.dataset.type === 'num';
      var dir = th.classList.contains('sorted')
        ? (th.dataset.dir==='asc'?'desc':'asc') : (num?'desc':'asc');
      headers.forEach(function(h){ h.classList.remove('sorted');
        var c=h.querySelector('.caret'); if(c) c.textContent='▲'; });
      th.classList.add('sorted'); th.dataset.dir=dir;
      th.querySelector('.caret').textContent = dir==='asc'?'▲':'▼';
      var rows = [].slice.call(table.rows).slice(1);
      rows.sort(function(a,b){
        if (num){
          var va=numval(a.cells[col]), vb=numval(b.cells[col]);
          var na=isNaN(va), nb=isNaN(vb);
          if(na&&nb) return 0; if(na) return 1; if(nb) return -1;
          return dir==='asc' ? va-vb : vb-va;
        }
        var xa=textval(a.cells[col]), xb=textval(b.cells[col]);
        if(xa===''&&xb==='') return 0; if(xa==='') return 1; if(xb==='') return -1;
        var cmp = xa.localeCompare(xb);
        return dir==='asc' ? cmp : -cmp;
      });
      var body = table.tBodies[0] || table;
      rows.forEach(function(r){ body.appendChild(r); });
    });
  });
});
})();
</script>"""




def _avg(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _pct(vals, p: float):
    """Linear-interpolated percentile."""
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    k = (len(vals) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def _fmt_score(v: float) -> str:
    """Every score to 3 decimals, so a non-perfect never rounds up to a fake
    '1.00' and two models near the saturated top stay distinguishable."""
    return f"{v:.3f}"


def _score_cell(v: float | None) -> str:
    if v is None:
        return '<span class="muted">—</span>'
    st = "good" if v >= 0.8 else ("warn" if v >= 0.4 else "crit")
    return (f'<span class="scv {st}">{_heat_swatch(v)}'
            f'<b>{_fmt_score(v)}</b></span>')


def _att_per_pass(rs: list[dict]) -> dict:
    """attempts / perfect-passes. Perfect = score exactly 1.0. Returns the
    ratio value, a formatted string, and a raw-count context string."""
    attempts = sum(r.get("n_attempts") or 1 for r in rs)
    scored = [r["score"]["score"] for r in rs
              if r["score"].get("status") == "scored"]
    perfect = sum(1 for v in scored if v >= 0.999)
    ratio = attempts / perfect if perfect else None
    return {
        "att_per_pass_val": ratio,
        "att_per_pass": f"{ratio:.2f}" if ratio is not None else "—",
        "app_ctx": f"{attempts} att · {perfect}/{len(scored)}"
                   if scored else "—",
        "n_perfect": perfect,
    }


def _model_summary(run: dict, model: str) -> dict:
    rs = [r for r in run["results"] if r["model"] == model]
    return {"model": model, **_summarize(rs)}


def _summarize(rs: list[dict]) -> dict:
    """Aggregate any set of task results into the summary-row metrics."""
    scored = [r["score"]["score"] for r in rs if r["score"].get("status") == "scored"]
    avg = _avg(scored)
    score_se = score_ci95 = None
    if len(scored) >= 2:
        import statistics as _st
        score_se = _st.stdev(scored) / (len(scored) ** 0.5)
        score_ci95 = 1.96 * score_se
    scored_pairs = [(r["score"]["score"], r.get("task", "")) for r in rs
                    if r["score"].get("status") == "scored"]
    lowest_val, lowest_task = min(scored_pairs) if scored_pairs else (None, "")
    ttfts = [a["ttft_ms"] for r in rs for a in r["attempts"] if a.get("ttft_ms")]
    tps = _avg([r.get("gen_tokens_per_sec") for r in rs])
    prefill = _avg([r.get("prefill_tokens_per_sec") for r in rs])
    tin = sum(r["tokens_in"] or 0 for r in rs)
    tout = sum(r["tokens_out"] or 0 for r in rs)
    cost = sum(r["cost_usd"] or 0 for r in rs)
    newest = max(rs, key=lambda r: r.get("started") or "") if rs else {}
    cold = newest.get("model_meta", {}).get("cold_start_ms")
    local = newest.get("model_meta", {}).get("local")
    gpu = newest.get("model_meta", {}).get("gpu") or {}
    gq = newest.get("model_meta", {}).get("gateway_quants") or {}

    scored_rs = [r for r in rs if r["score"].get("status") == "scored"]
    first_try = (sum(1 for r in scored_rs
                     if r["score"]["score"] == 1.0 and r["n_retries"] == 0)
                 / len(scored_rs)) if scored_rs else None
    score_sum = sum(r["score"]["score"] for r in scored_rs)
    wall_min = sum(r["wall_ms"] for r in rs) / 60000 if rs else 0
    score_per_min = score_sum / wall_min if wall_min > 0 else None

    energy_wh = gpu.get("energy_wh")
    energy_usd = _energy_usd(energy_wh)
    eff_cost = (energy_usd if local and energy_usd else cost)
    score_per_dollar = score_sum / eff_cost if eff_cost > 0 else None
    walls = [r["wall_ms"] for r in rs]
    return {
        "avg_score_val": avg,
        "score_se": score_se,
        "score_ci95": score_ci95,
        "n_scored_tasks": len(scored),
        "lowest_val": lowest_val,
        "lowest_task": lowest_task,
        "chip": _score_cell(avg),
        "pending": sum(1 for r in rs if r["score"].get("status") == "pending"),
        "errors": sum(1 for r in rs if r["status"] != "ok"),
        "wall": fmt_ms(sum(r["wall_ms"] for r in rs)),
        "ttft": fmt_ms(_avg(ttfts)),
        "tps": f"{tps:.1f}" if tps else "—",
        "tps_val": tps,
        "prefill": f"{prefill:,.0f}" if prefill else "—",
        "quant": (newest.get("model_meta", {}).get("model_info") or {}).get(
            "quantization"),
        "tokens": f"{tin:,} / {tout:,}",
        "tokens_total": tin + tout,
        "cost": (f"{fmt_cost(eff_cost)} ⚡" if local and energy_usd
                 else fmt_cost(cost)),
        "cost_val": eff_cost,
        "api_cost_val": cost,
        "retries": sum(r["n_retries"] for r in rs),
        "tries": sum(r.get("n_attempts") or 1 for r in rs),
        "wall_ms_sum": sum(r["wall_ms"] for r in rs),
        **_att_per_pass(rs),
        "cold": fmt_ms(cold),
        "local": local,
        "first_try": f"{first_try:.0%}" if first_try is not None else "—",
        "first_try_val": first_try,
        "score_per_min": (f"{score_per_min:.2f}"
                          if score_per_min is not None else "—"),
        "score_per_min_val": score_per_min,
        "score_per_dollar": (f"{score_per_dollar:,.1f}"
                             if score_per_dollar is not None else "—"),
        "score_per_dollar_val": score_per_dollar,
        "p50": fmt_ms(_pct(walls, 50)),
        "p95": fmt_ms(_pct(walls, 95)),
        "vram": (f"{gpu['vram_peak_mb']:,} MB" if gpu.get("vram_peak_mb") else "—"),
        "watts": (f"{gpu['power_avg_w']:.0f} W" if gpu.get("power_avg_w") else "—"),
        "energy": (f"{gpu['energy_wh']:.2f} Wh" if gpu.get("energy_wh") else "—"),
        "energy_cost": _energy_cost(gpu.get("energy_wh")),
        "energy_wh_val": gpu.get("energy_wh"),
        "hosts": [
            (f"{h} ({gq[h]})" if gq.get(h) and gq[h] != "unknown" else h)
            for h in sorted({h for r in rs
                             for h in (r.get("served_by") or [])})],
        "billed": any(r.get("cost_source") == "billed" for r in rs),
    }


def _power_cfg() -> dict:
    try:
        from .fit import load_directives
        return load_directives().get("power") or {}
    except Exception:
        return {}


def _energy_usd(energy_wh) -> float:
    """Measured GPU energy -> money at the configured rate. 0 when unknown."""
    if not energy_wh:
        return 0.0
    rate = _power_cfg().get("cost_per_kwh")
    if not rate:
        return 0.0
    return (energy_wh / 1000.0) * float(rate)


def _energy_cost(energy_wh) -> str:
    """GPU energy -> money at the directives.yaml rate. Marginal and GPU-only
    (excludes CPU/RAM/board/PSU) and ignores hardware amortisation — a floor on
    what the machine pulls, not a utility bill."""
    if not energy_wh:
        return "—"
    cfg = _power_cfg()
    rate = cfg.get("cost_per_kwh")
    if not rate:
        return "—"
    cur = cfg.get("currency", "$")
    cost = (energy_wh / 1000.0) * float(rate)
    return f"{cur}{cost:.3f}" if cost < 0.1 else f"{cur}{cost:.2f}"


def _model_ids() -> dict[str, str]:
    """name -> the concrete model id it runs (the label vs the thing actually
    measured — e.g. "claude-cli-sonnet" running claude-sonnet-4-6)."""
    try:
        from .registry import load_models
        return {m.name: m.model for m in load_models(include_disabled=True)}
    except Exception:
        return {}


def _leader_key(summaries: dict):
    """Ranking: score desc, then cost asc, then speed desc."""
    def key(m: str):
        s = summaries[m]
        return (-(s["avg_score_val"] if s["avg_score_val"] is not None else -1),
                s["cost_val"] or 0,
                -(s["tps_val"] or 0))
    return key


def _pre_v05_caveat(dataset_key: str) -> str:
    """Honesty banner for archived datasets scored before the v0.5 methodology
    fixes. Empty for the live set and 0.5+ archives."""
    try:
        parts = tuple(int(x) for x in str(dataset_key).split("."))
    except (ValueError, AttributeError):
        return ""
    if parts >= (0, 5):
        return ""
    return ("This archived dataset predates the v0.5 methodology fixes: the "
            "no-op-floor redesign (v0.5.5–0.5.6) and the timing-budget "
            "calibration (v0.5.9). Weak-model scores on agentic and "
            "timing-sensitive tasks can be over-credited here. Ranks remain "
            "the honest cross-version comparison; raw scores are not comparable "
            "across versions. See the CHANGELOG for details.")


def leaderboard(runs: list[dict] | None = None,
                tasks_dir: Path | None = None) -> list[dict]:
    """The canonical standings — every run per model·task aggregated, ranked. One
    aggregation and ranking key for both the overview and the content pipeline.

    A model that hasn't attempted the whole suite is NOT ranked: its mean isn't
    comparable, and the tasks it's missing skew toward the ones it failed. Those
    are still returned with `rank: None` and `partial: True`, shown but not
    ranked.
    """
    runs = load_all_runs() if runs is None else runs
    _, hidden = _model_prefs()
    all_models = sorted({res["model"] for r in runs for res in r["results"]}
                        - hidden)
    tdefs = _task_defs(tasks_dir)
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    by_model: dict[str, list[dict]] = {}
    for info in task_data.values():
        for m, e in info["agg"].items():
            by_model.setdefault(m, []).append(e)
    summaries = {m: {"model": m, **_summarize(by_model.get(m, []))}
                 for m in all_models}

    n_suite = len(tdefs) or 1
    ordered = sorted(all_models, key=_leader_key(summaries))
    complete = [m for m in ordered if len(by_model.get(m, [])) >= n_suite]
    partial = [m for m in ordered if len(by_model.get(m, [])) < n_suite]

    out = []
    for i, m in enumerate(complete):
        n = len(by_model.get(m, []))
        out.append({"rank": i + 1, "n_tasks": n, "n_suite": n_suite,
                    "coverage": n / n_suite, "partial": False, **summaries[m]})
    for m in partial:
        n = len(by_model.get(m, []))
        out.append({"rank": None, "n_tasks": n, "n_suite": n_suite,
                    "coverage": n / n_suite, "partial": True, **summaries[m]})
    return out


_MEAN_FIELDS = ("wall_ms", "tokens_in", "tokens_out", "cost_usd",
                "gen_tokens_per_sec", "prefill_tokens_per_sec",
                "reasoning_tokens", "n_retries")


def _runs_badge(n_runs: int, n_scored: int, run_ids: list[str]) -> tuple[str, str]:
    """The ×N aggregate badge + tooltip. The score is the mean of the SCORED
    runs only, so when some runs didn't score (crash/spiral/DNF) the badge reads
    scored/total (e.g. ×2/3) rather than implying all 3 counted toward it."""
    if n_runs <= 1:
        return "", ""
    ids = ", ".join(run_ids)
    if n_scored >= n_runs:
        return f"×{n_runs}", f"score = mean of {n_runs} runs: {ids}"
    return (f"×{n_scored}/{n_runs}",
            f"score = mean of {n_scored} scored of {n_runs} runs "
            f"({n_runs - n_scored} unscored, left out): {ids}")


def _aggregate(entries: list[dict]) -> dict:
    """Every run of one model·task in this dataset, as a single result.

    Testing again does not replace the old number, it flattens into it: the
    score is the MEAN of every scored run. Unscored runs (crash, spiral, DNF)
    are left out of the mean, matching _summarize, which counts only
    status=="scored" toward a model's average — an error must not silently
    become a 0 here when it isn't one there.

    Shaped exactly like a single result so every consumer reads it unchanged,
    plus n_runs/score_sigma/run_ids for pages that want to show the spread.
    """
    import statistics
    newest = entries[-1]
    n_scored = sum(1 for e in entries
                   if e["score"].get("status") == "scored"
                   and e["score"].get("score") is not None)
    agg = {**newest, "n_runs": len(entries), "n_scored": n_scored,
           "run_ids": [e["run_id"] for e in entries], "score_sigma": None}
    if len(entries) == 1:
        return agg
    vals = [e["score"]["score"] for e in entries
            if e["score"].get("status") == "scored"
            and e["score"].get("score") is not None]
    if vals:
        agg["score"] = {**next(e["score"] for e in reversed(entries)
                               if e["score"].get("status") == "scored"),
                        "score": statistics.fmean(vals)}
        agg["score_sigma"] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    for k in _MEAN_FIELDS:
        nums = [e[k] for e in entries if e.get(k) is not None]
        if nums:
            agg[k] = statistics.fmean(nums)
    agg["attempts"] = [a for e in entries for a in e.get("attempts") or []]
    return agg


def _consistency(model: str, task_data: dict) -> dict:
    """How reproducible is this model, and where is it least so?

    Mean of the per-task σ over the tasks run more than once, plus the single
    worst task by name. The old measure was the spread of a model's whole-SUITE
    average between runs, which answers nothing: it is empty until a model has
    two runs, and once it has two it compares a 42-task pass against a 5-task
    re-run of the hard ones and calls the difference "inconsistency". Spread is
    only meaningful against the SAME task.

    A task run 3× that never moved (σ 0.000) is a real result and must not read
    the same as one never repeated ("—").
    """
    import statistics
    wobble = sorted(
        ((e["score_sigma"], tid) for tid, info in task_data.items()
         if (e := info["agg"].get(model)) and e.get("n_runs", 1) > 1
         and e.get("score_sigma") is not None),
        reverse=True)
    if not wobble:
        return {"sigma": "—", "sigma_sort": "", "sigma_note": "no task re-run yet",
                "sigma_title": ("Nothing has been measured twice, so there is no "
                                "spread to report. Re-run the suite (harness run "
                                "--repeat N) and the repeats aggregate into each "
                                "score."),
                "worst": "—"}
    mean_sig = statistics.fmean(sg for sg, _t in wobble)
    unstable = [f"{t} ±{sg:.3f}" for sg, t in wobble if sg > 0][:5]
    return {
        "sigma": f"±{mean_sig:.3f}",
        "sigma_sort": f"{mean_sig:.6f}",
        "sigma_note": f"{len(wobble)} task{'s' if len(wobble) != 1 else ''} re-run",
        "sigma_title": ("mean per-task σ over the tasks run more than once. "
                        + (f"Least stable: {'; '.join(unstable)}" if unstable
                           else "Every re-run scored identically.")),
        "worst": (f"{wobble[0][1]} ±{wobble[0][0]:.3f}"
                  if wobble[0][0] > 0 else "—"),
    }


def collect_task_data(runs: list[dict]) -> dict[str, dict]:
    """task_id -> aggregated result per model + full history, across all runs.

    `agg` is the basis for every page. A model·task measured more than once in a
    dataset aggregates (see _aggregate) — it is not the newest run.
    """
    data: dict[str, dict] = {}
    per: dict[tuple[str, str], list[dict]] = {}
    for r in runs:
        for res in r["results"]:
            t = data.setdefault(res["task"], {
                "category": res["category"], "tier": res["tier"],
                "agg": {}, "history": []})
            entry = {**res, "run_id": r["run_id"]}
            t["history"].append(entry)
            per.setdefault((res["task"], res["model"]), []).append(entry)
    for (tid, model), entries in per.items():
        data[tid]["agg"][model] = _aggregate(entries)
    return data


def _task_defs(tasks_dir: Path | None = None) -> dict:
    try:
        from .tasks import load_tasks
        return {t.id: t for t in load_tasks(tasks_dir or config.TASKS_DIR)}
    except Exception:
        return {}


def _model_prefs() -> tuple[dict, set]:
    """(color overrides, hidden models) from the registry yamls. Historical
    models with no yaml keep defaults: auto color, shown."""
    try:
        from .registry import load_models
        models = load_models(include_disabled=True)
        colors = {m.name: m.color for m in models
                  if m.color and m.color.startswith("#")}
        hidden = {m.name for m in models if not m.show_in_reports}
        return colors, hidden
    except Exception:
        return {}, set()


def _hex_to_hsl(hexc: str) -> tuple[float, float, float] | None:
    """'#rrggbb' -> (h 0-360, s 0-100, l 0-100), or None if unparseable."""
    h = (hexc or "").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except (ValueError, IndexError):
        return None
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    lum = (mx + mn) / 2
    if d == 0:
        hue = 0.0
    elif mx == r:
        hue = ((g - b) / d) % 6
    elif mx == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    sat = 0.0 if d == 0 else d / (1 - abs(2 * lum - 1))
    return hue * 60, sat * 100, lum * 100


def _model_colors(order: list[str], overrides: dict,
                  families: dict | None = None,
                  family_colors: dict | None = None) -> dict[str, str]:
    """One color per model, used by every chart. A per-model yaml override wins.
    Otherwise, with `families` given, colour BY FAMILY: a manual family colour
    shades across its members; a family (or no-family singleton) without one gets
    an auto golden-angle hue clear of the manual hues. Without `families`, fall
    back to the fixed palette slots (historical data)."""
    colors = {}
    if families is not None:
        family_colors = family_colors or {}
        seq, members = [], {}
        for m in order:
            f = families.get(m) or m
            if f not in members:
                seq.append(f)
                members[f] = []
            members[f].append(m)
        manual_hsl = {}
        for f in seq:
            hexc = (family_colors.get(f) or {}).get("color")
            hsl = _hex_to_hsl(hexc) if hexc else None
            if hsl:
                manual_hsl[f] = hsl
        taken = [h for h, _, _ in manual_hsl.values()]
        auto_hue, step = {}, 0
        for f in seq:
            if f in manual_hsl:
                continue
            h = (step * 137.508) % 360
            while any(min(abs(h - t), 360 - abs(h - t)) < 12 for t in taken):
                step += 1
                h = (step * 137.508) % 360
            auto_hue[f] = h
            taken.append(h)
            step += 1
        for m in order:
            if m in overrides:
                colors[m] = overrides[m]
                continue
            f = families.get(m) or m
            mem = members[f]
            k, idx = len(mem), mem.index(m)
            t = 0.5 if k == 1 else idx / (k - 1)
            span = min(18.0, k * 4.0)
            if f in manual_hsl:
                if k == 1:
                    colors[m] = (family_colors.get(f) or {})["color"]
                    continue
                hue, sat, lum = manual_hsl[f]
                light = max(30.0, min(78.0, lum + (t - 0.5) * span))
                colors[m] = f"hsl({hue:.0f} {sat:.0f}% {light:.0f}%)"
            else:
                light = max(34.0, min(70.0, 54 + (t - 0.5) * span))
                colors[m] = f"hsl({auto_hue[f]:.0f} 62% {light:.0f}%)"
        return colors
    slot = 0
    for m in order:
        if m in overrides:
            colors[m] = overrides[m]
        else:
            colors[m] = f"var(--s{(slot % PALETTE_N) + 1})"
            slot += 1
    return colors


def load_versions() -> list[tuple]:
    """Every dataset version (archives + live), chronological, each as
    (key, task_data, tdefs). The shared basis for every cross-version view —
    load it ONCE and pass it down; it reads all archives + live runs."""
    from .archive import list_archives
    specs = []
    for a in list_archives():
        base = config.ARCHIVE_DIR / f"v{a['key']}"
        specs.append((a["key"], base / "runs",
                      base / "tasks" if (base / "tasks").is_dir() else None))
    live_key = ".".join(config.suite_version().split(".")[:2])
    specs.append((live_key, config.RUNS_DIR, config.TASKS_DIR))
    specs.sort(key=lambda v: tuple(int(x) for x in v[0].split(".")))
    out = []
    for key, runs_dir, tasks_dir in specs:
        runs = load_all_runs(runs_dir)
        if not runs:
            continue
        tdefs = _task_defs(tasks_dir)
        td = {tid: info for tid, info in collect_task_data(runs).items()
              if tid in tdefs}
        if td:
            out.append((key, td, tdefs))
    return out


def version_rankings(versions: list[tuple] | None = None) -> list[dict]:
    """Leaderboard rank per model for every version. Ranks are comparable across
    versions, scores aren't. Feeds the bump chart. Returns
    [{key, n_models, ranks: {model: {rank, score}}}]."""
    versions = versions if versions is not None else load_versions()
    _, hidden = _model_prefs()
    out = []
    for key, task_data, _tdefs in versions:
        scores: dict[str, list[float]] = {}
        for info in task_data.values():
            for m, e in info["agg"].items():
                if m in hidden or e["score"].get("status") != "scored":
                    continue
                scores.setdefault(m, []).append(e["score"]["score"])
        if not scores:
            continue
        avg = {m: sum(v) / len(v) for m, v in scores.items()}
        ordered = sorted(avg.items(), key=lambda kv: (-round(kv[1], 4), kv[0]))
        ranks, rank, prev = {}, 0, None
        for i, (m, s) in enumerate(ordered):
            if prev is None or round(s, 4) < prev:
                rank = i + 1
            prev = round(s, 4)
            ranks[m] = {"rank": rank, "score": s}
        out.append({"key": key, "n_models": len(ranks), "ranks": ranks})
    return out


_VERDICT_EPS = 0.005


def _verdict(delta) -> str:
    if delta is None:
        return "na"
    if delta > _VERDICT_EPS:
        return "better"
    if delta < -_VERDICT_EPS:
        return "worse"
    return "flat"


def _model_scores(model: str, task_data: dict, tdefs: dict) -> dict:
    """{tid: (score, content_hash, category)} for a model's SCORED tasks in a
    version — the raw material for a like-for-like version diff."""
    out = {}
    for tid, info in task_data.items():
        e = info["agg"].get(model)
        if not e or e["score"].get("status") != "scored" \
                or e["score"].get("score") is None:
            continue
        td = tdefs.get(tid)
        if not td:
            continue
        out[tid] = (e["score"]["score"], getattr(td, "content_hash", ""),
                    td.category)
    return out


def version_diff(model, tdA, tdefsA, tdB, tdefsB, key_a="", key_b=""):
    """One model, version A -> B. Compares only tasks the model was scored on in
    BOTH versions, split into 'identical' (same content_hash — a true
    like-for-like) and 'changed' (same id, edited test — delta is not
    trustworthy). Headline numbers use identical tasks only. Returns None if the
    model isn't present in both versions."""
    A = _model_scores(model, tdA, tdefsA)
    B = _model_scores(model, tdB, tdefsB)
    if not A or not B:
        return None
    tasks = []
    for tid in sorted(set(A) & set(B)):
        a_sc, a_h, cat = A[tid]
        b_sc, b_h, _ = B[tid]
        tier = "identical" if (a_h and b_h and a_h == b_h) else "changed"
        tasks.append({"tid": tid, "cat": cat, "a": round(a_sc, 4),
                      "b": round(b_sc, 4), "delta": round(b_sc - a_sc, 4),
                      "tier": tier})
    ident = [t for t in tasks if t["tier"] == "identical"]

    def _mean(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    mA, mB = _mean([t["a"] for t in ident]), _mean([t["b"] for t in ident])
    delta = round(mB - mA, 4) if (mA is not None and mB is not None) else None
    cats: dict[str, list] = {}
    for t in ident:
        cats.setdefault(t["cat"], []).append(t)
    cat_rows = []
    for c in sorted(cats):
        ca, cb = _mean([t["a"] for t in cats[c]]), _mean([t["b"] for t in cats[c]])
        cd = round(cb - ca, 4) if (ca is not None and cb is not None) else None
        cat_rows.append({"cat": c, "a": ca, "b": cb, "delta": cd,
                         "verdict": _verdict(cd), "n": len(cats[c])})
    return {
        "model": model, "a": key_a, "b": key_b,
        "overall": {"a": mA, "b": mB, "delta": delta,
                    "verdict": _verdict(delta), "n": len(ident)},
        "cats": cat_rows, "tasks": tasks,
        "coverage": {
            "added": [{"tid": t, "cat": B[t][2]} for t in sorted(set(B) - set(A))],
            "retired": [{"tid": t, "cat": A[t][2]} for t in sorted(set(A) - set(B))],
            "changed": [t["tid"] for t in tasks if t["tier"] == "changed"],
        },
    }


def family_version_diff(family, members, tdA, tdefsA, tdB, tdefsB, key_a="", key_b=""):
    """A whole family, version A -> B. Rolls up each member's version_diff over
    the members present in BOTH versions (a new member never counts as
    improvement), pooling identical-task scores for the family/category numbers.
    Returns None if no member spans both versions."""
    mrows, pool = [], []
    added_m, dropped_m = [], []
    for m in sorted(members):
        md = version_diff(m, tdA, tdefsA, tdB, tdefsB, key_a, key_b)
        if not md:
            inA = bool(_model_scores(m, tdA, tdefsA))
            inB = bool(_model_scores(m, tdB, tdefsB))
            if inB and not inA:
                added_m.append(m)
            elif inA and not inB:
                dropped_m.append(m)
            continue
        mrows.append({"model": m, "a": md["overall"]["a"], "b": md["overall"]["b"],
                      "delta": md["overall"]["delta"],
                      "verdict": md["overall"]["verdict"]})
        pool += [(t["a"], t["b"], t["cat"]) for t in md["tasks"]
                 if t["tier"] == "identical"]
    if not mrows:
        return None

    def _m(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    fa, fb = _m([p[0] for p in pool]), _m([p[1] for p in pool])
    fd = round(fb - fa, 4) if (fa is not None and fb is not None) else None
    catmap: dict[str, list] = {}
    for a, b, c in pool:
        catmap.setdefault(c, []).append((a, b))
    cat_rows = []
    for c in sorted(catmap):
        ca, cb = _m([p[0] for p in catmap[c]]), _m([p[1] for p in catmap[c]])
        cd = round(cb - ca, 4) if (ca is not None and cb is not None) else None
        cat_rows.append({"cat": c, "a": ca, "b": cb, "delta": cd,
                         "verdict": _verdict(cd), "n": len(catmap[c])})
    mrows.sort(key=lambda r: (r["delta"] if r["delta"] is not None else 0.0))
    return {
        "family": family, "a": key_a, "b": key_b,
        "overall": {"a": fa, "b": fb, "delta": fd, "verdict": _verdict(fd),
                    "n_members": len(mrows), "n_tasks": len(pool)},
        "cats": cat_rows, "members": mrows,
        "coverage": {"added_members": added_m, "dropped_members": dropped_m},
    }


def _all_pairs(present: list[tuple], diff_fn) -> dict:
    """Every version pair (a<b) among `present` [(key, td, tdefs)...] -> diff,
    keyed 'a|b'. Empty/None diffs are dropped so the picker only offers real
    comparisons."""
    pairs = {}
    for i in range(len(present)):
        for j in range(i + 1, len(present)):
            ka, tda, tdefa = present[i]
            kb, tdb, tdefb = present[j]
            d = diff_fn(tda, tdefa, tdb, tdefb, ka, kb)
            if d:
                pairs[f"{ka}|{kb}"] = d
    return pairs


def model_version_payload(model: str, versions: list[tuple]) -> dict:
    """{versions:[keys the model appears in], pairs:{'a|b': version_diff}}."""
    present = [(k, td, tdefs) for (k, td, tdefs) in versions
               if _model_scores(model, td, tdefs)]
    pairs = _all_pairs(present, lambda *a: version_diff(model, *a))
    return {"versions": [k for k, _t, _d in present], "pairs": pairs}


def family_version_payload(family: str, members: set, versions: list[tuple]) -> dict:
    present = [(k, td, tdefs) for (k, td, tdefs) in versions
               if any(_model_scores(m, td, tdefs) for m in members)]
    pairs = _all_pairs(present,
                       lambda *a: family_version_diff(family, members, *a))
    return {"versions": [k for k, _t, _d in present], "pairs": pairs}


def _family_of_map(versions: list[tuple]) -> dict:
    """model name -> family, for every model across all versions (registry yaml
    wins; else inferred from the name)."""
    from .registry import infer_family, load_models
    reg = {m.name: m for m in load_models(include_disabled=True)}
    names = {mm for _k, td, _t in versions for info in td.values()
             for mm in info["agg"]}
    out = {}
    for n in names:
        m = reg.get(n)
        out[n] = m.family_name if m else infer_family(n, n)
    return out


def bump_chart(versions: list[dict], colors: dict[str, str],
               width=1120) -> str:
    """Rank-trajectory (bump) chart across suite versions. Solid = present in
    every version, faded = partial coverage."""
    if len(versions) < 2:
        return ""
    models = sorted({m for v in versions for m in v["ranks"]})
    if not models:
        return ""
    latest = versions[-1]["ranks"]
    in_all = {m for m in models
              if all(m in v["ranks"] for v in versions)}
    max_rank = max(r["rank"] for v in versions for r in v["ranks"].values())
    left, right, top, bottom = 60, 250, 34, 16
    row_h = 26
    height = top + bottom + row_h * max(max_rank - 1, 1) + 10

    def X(i):
        span = width - left - right
        return left + (span * i / max(len(versions) - 1, 1))

    def Y(rank):
        return top + (rank - 1) * row_h

    parts = [f'<svg class="bump" viewBox="0 0 {width} {height}" '
             f'style="width:100%;height:auto" role="img" '
             f'aria-label="model rankings across suite versions">']
    for i, v in enumerate(versions):
        parts.append(
            f'<text x="{X(i):.0f}" y="16" text-anchor="middle" '
            f'style="font:600 12px system-ui;fill:var(--muted)">v{v["key"]} '
            f'({v["n_models"]})</text>')
    for r in range(1, max_rank + 1):
        parts.append(f'<text x="{left - 34}" y="{Y(r) + 4:.0f}" '
                     f'style="font:11px system-ui;fill:var(--muted)">#{r}</text>')
    label_ys: list[float] = []
    node_models: dict[tuple, list] = {}
    node_names: dict[tuple, list] = {}
    for m in sorted(models, key=lambda m: versions[-1]["ranks"]
                    .get(m, {"rank": 99})["rank"]):
        slug = _slug_name(m)
        color = colors.get(m, "var(--accent)")
        solid = m in in_all
        pts = [(i, v["ranks"][m]["rank"]) for i, v in enumerate(versions)
               if m in v["ranks"]]
        segs, seg = [], [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if b[0] == a[0] + 1:
                seg.append(b)
            else:
                segs.append(seg)
                seg = [b]
        segs.append(seg)
        parts.append(f'<g class="bm" data-m="{slug}"'
                     + ("" if solid else ' opacity=".4"') + '>')
        dash = "" if solid else ";stroke-dasharray:5 4"
        for s in segs:
            if len(s) > 1:
                d = " ".join(f'{"M" if j == 0 else "L"}{X(i):.0f},{Y(r):.0f}'
                             for j, (i, r) in enumerate(s))
                parts.append(f'<path d="{d}" style="stroke:{color};'
                             f'stroke-width:2.5;fill:none;stroke-linecap:round'
                             f'{dash}"/>')
        for i, r in pts:
            parts.append(f'<circle cx="{X(i):.0f}" cy="{Y(r):.0f}" r="8.5" '
                         f'fill="{color}"/>')
            parts.append(f'<text x="{X(i):.0f}" y="{Y(r) + 3.5:.0f}" '
                         f'text-anchor="middle" style="font:700 10px '
                         f'system-ui;fill:#fff">{r}</text>')
            node_models.setdefault((i, r), []).append(slug)
            node_names.setdefault((i, r), []).append(m)
        if m in latest:
            li, lr = pts[-1]
            ly = Y(lr)
            while any(abs(ly - o) < 13 for o in label_ys):
                ly += 13
            label_ys.append(ly)
            score = versions[li]["ranks"][m]["score"]
            parts.append(f'<text class="bmlabel" x="{X(li) + 14:.0f}" '
                         f'y="{ly + 4:.0f}" style="font:600 11.5px system-ui;'
                         f'fill:{color}">{html.escape(m)} · {score:.3f}</text>')
        parts.append("</g>")
    for (i, r), slugs in node_models.items():
        names = html.escape(", ".join(node_names[(i, r)]))
        parts.append(f'<circle class="bmhit" cx="{X(i):.0f}" cy="{Y(r):.0f}" '
                     f'r="13" fill="transparent" '
                     f'data-ms="{",".join(slugs)}"><title>{names}</title>'
                     f'</circle>')
    parts.append("</svg>")
    return "".join(parts)


def _rank_key(entry: dict):
    s = entry["score"].get("score") if entry["score"].get("status") == "scored" else None
    return (-(s if s is not None else -1),
            entry.get("cost_usd") or 0,
            -(entry.get("gen_tokens_per_sec") or 0))


def build_task_report(task_id: str, info: dict, tdef,
                      acfg: dict | None = None, suspect: dict | None = None) -> str:
    results = sorted(info["agg"].values(), key=_rank_key)
    rows = []
    tout_max = max((e["tokens_out"] or 0) for e in results) or 1
    for e in results:
        ttfts = [a["ttft_ms"] for a in e["attempts"] if a.get("ttft_ms")]
        cls = diagnose(e, tdef, acfg, suspect)
        rows.append({
            "model": e["model"], "model_link": _mlink(e["model"], prefix="../"),
            "slug": _slug_name(e["model"]),
            "run_id": e["run_id"],
            "files": (f"/data/{quote(e['run_id'])}/{quote(e['model'])}"
                      f"/{quote(task_id)}/"),
            "n_runs": e.get("n_runs", 1),
            "n_scored": e.get("n_scored", e.get("n_runs", 1)),
            "runs_title": ", ".join(e.get("run_ids") or [e["run_id"]]),
            "nrun_badge": _runs_badge(e.get("n_runs", 1),
                                      e.get("n_scored", e.get("n_runs", 1)),
                                      e.get("run_ids") or [e["run_id"]])[0],
            "nrun_title": _runs_badge(e.get("n_runs", 1),
                                      e.get("n_scored", e.get("n_runs", 1)),
                                      e.get("run_ids") or [e["run_id"]])[1],
            "sigma": (f"±{e['score_sigma']:.3f}"
                      if e.get("score_sigma") is not None
                      and e.get("n_runs", 1) > 1 else ""),
            "chip": score_chip(e["score"]),
            "fail": _fail_badge(e),
            "why": why_cell(cls),
            "why_full": html.escape(cls["detail"]) if cls else "",
            "wall": fmt_ms(e["wall_ms"]),
            "ttft": fmt_ms(_avg(ttfts)),
            "tin": fmt_tok(e["tokens_in"]), "tout": fmt_tok(e["tokens_out"]),
            "tout_bar": bar(e["tokens_out"] or 0, tout_max, width=90),
            "tps": (f"{e['gen_tokens_per_sec']:.1f}"
                    if e.get("gen_tokens_per_sec") else "—"),
            "cost": fmt_cost(e.get("cost_usd")),
            "retries": e["n_retries"],
            "summary": html.escape(
                f"{e['score'].get('summary') or e['score'].get('status')} · "
                f"{fmt_ms(e['wall_ms'])} · {fmt_tok(e['tokens_out'])} tok out"
                + (f" · {fmt_tok(e['reasoning_tokens'])} think"
                   if e.get("reasoning_tokens") else "")),
            "output": html.escape(
                last_response_text(e["run_id"], e["model"], task_id)
                or "(no response captured)"),
        })

    scored = [e["score"]["score"] for e in results
              if e["score"].get("status") == "scored"]
    pass_thresh = (acfg or {}).get("pass_threshold", 0.8)
    passers = [e for e in results if e["score"].get("status") == "scored"
               and (e["score"].get("score") or 0) >= pass_thresh]
    p_walls = [e["wall_ms"] for e in passers if e.get("wall_ms")]
    p_touts = [e["tokens_out"] for e in passers if e.get("tokens_out")]
    tiles = [
        {"v": str(len(results)), "k": "models tested"},
        {"v": f"{max(scored):.3f}" if scored else "—", "k": "best score"},
        {"v": fmt_ms(min(p_walls)) if p_walls else "—", "k": "fastest (passed)"},
        {"v": fmt_tok(min(p_touts)) if p_touts else "—",
         "k": "fewest tokens (passed)"},
        {"v": str(len(info["history"])), "k": "total results"},
    ]

    history = [{
        "run_id": e["run_id"], "model": _mlink(e["model"], prefix="../"),
        "chip": score_chip(e["score"]),
        "wall": fmt_ms(e["wall_ms"]),
        "tokens": f"{fmt_tok(e['tokens_in'])} / {fmt_tok(e['tokens_out'])}",
        "cost": fmt_cost(e.get("cost_usd")),
    } for e in reversed(info["history"])]

    return _env.from_string(TASK_TEMPLATE).render(
        nav=_nav("../"),
        sort_js=_SORT_JS, focus_js=_FOCUS_JS,
        files_col=(_RUNS_BASE == config.RUNS_DIR),
        css=BASE_CSS, task_id=task_id,
        title=html.escape(tdef.title) if tdef else task_id,
        category=info["category"], tier=info["tier"],
        scoring_type=(tdef.scoring_type if tdef else "?"),
        task_hash=(tdef.content_hash if tdef else info["history"][-1]["task_hash"]),
        prompt=html.escape(tdef.prompt) if tdef else "",
        tiles=tiles, rows=rows, history=history)


def build_run_report(run: dict, tdefs: dict | None = None) -> str:
    tdefs = tdefs if tdefs is not None else _task_defs()
    models = [m for m in run["manifest"]["models"]
              if any(r["model"] == m for r in run["results"])]
    summaries = [{**_model_summary(run, m), "model_link": _mlink(m, "../")}
                 for m in models]

    total_tokens = sum(s["tokens_total"] for s in summaries)
    total_cost = sum(r["cost_usd"] or 0 for r in run["results"])
    pending = sum(s["pending"] for s in summaries)
    scored_avg = _avg([s["avg_score_val"] for s in summaries])
    tiles = [
        {"v": f"{scored_avg:.3f}" if scored_avg is not None else "—", "k": "avg score"},
        {"v": str(len(models)), "k": "models"},
        {"v": str(len(run["manifest"]["tasks"])), "k": "tasks"},
        {"v": fmt_ms(sum(r["wall_ms"] for r in run["results"])), "k": "total wall"},
        {"v": f"{total_tokens:,}", "k": "tokens"},
        {"v": fmt_cost(total_cost), "k": "cost"},
        {"v": str(pending), "k": "pending review"},
    ]

    by_task: dict[str, dict] = {}
    for r in run["results"]:
        by_task.setdefault(r["task"], {"cat": r["category"], "tier": r["tier"],
                                       "cells": {}})["cells"][r["model"]] = r
    grid = []
    for task_id, info in sorted(by_task.items()):
        cells = []
        for m in models:
            r = info["cells"].get(m)
            if not r:
                cells.append({"chip": '<span class="muted">skipped</span>', "time": ""})
                continue
            tok = ""
            if r["tokens_out"] is not None:
                tok = f"{fmt_tok(r['tokens_in'])} / {fmt_tok(r['tokens_out'])} tok"
                if r.get("cost_usd"):
                    tok += f" · {fmt_cost(r['cost_usd'])}"
            cells.append({"chip": score_chip(r["score"]),
                          "time": fmt_ms(r["wall_ms"]), "tok": tok})
        grid.append({"task": task_id, "cat": info["cat"], "tier": info["tier"],
                     "cells": cells,
                     "linked": task_id in tdefs})

    details = []
    for r in sorted(run["results"], key=lambda x: (x["model"], x["task"])):
        details.append({
            "model": r["model"], "task": r["task"],
            "summary": html.escape(
                f"{r['score'].get('summary') or r['score'].get('status')} · "
                f"{fmt_ms(r['wall_ms'])} · {r['n_attempts']} attempt(s) · "
                f"{r['turns']} turn(s)"),
            "attempts": [{
                "n": a["n"], "ttft": fmt_ms(a.get("ttft_ms")),
                "total": fmt_ms(a.get("total_ms")),
                "tin": f"{a['tokens_in']:,}" if a.get("tokens_in") else "—",
                "tout": f"{a['tokens_out']:,}" if a.get("tokens_out") else "—",
                "stop": html.escape(str(a.get("stop_reason") or "—")),
                "err": html.escape(str(a.get("error") or "")[:120]),
            } for a in r["attempts"]],
            "detail": html.escape((r["score"].get("detail") or "")[:2000]),
            "path": f"runs/{run['run_id']}/{r['model']}/{r['task']}/transcript.jsonl",
        })

    env = run["manifest"].get("env") or {}
    env_line = " · ".join(filter(None, [env.get("gpu"), env.get("os", "")[:28]]))
    from . import assess
    ar = assess.assess_run(run, tdefs)
    _AN = {"model": "model", "harness": "harness", "infra": "infra",
           "known-limit": "limit"}
    run_rollup = {
        "pills": [{"cls": a, "name": _AN.get(a, a), "n": n}
                  for a, n in sorted(ar["by_attribution"].items(),
                                     key=lambda kv: -kv[1])],
        "recovered": ar["retries"]["recovered"], "fatal": ar["retries"]["fatal"],
    }
    return _env.from_string(RUN_TEMPLATE).render(
        nav=_nav("../"),
        sort_js=_SORT_JS,
        css=BASE_CSS, run_id=run["run_id"], manifest=run["manifest"],
        env_line=html.escape(env_line), run_rollup=run_rollup,
        tiles=tiles, summaries=summaries, models=models, grid=grid, details=details)


MODEL_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ model }} · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">
  <div><h1>{{ model }}</h1>
  <div class="sub">{{ where }} · {{ dataset_label or "live dataset" }} ·
  aggregated result per task across {{ n_runs }} run(s)
  {% for l in model_links %}<a class="reflink" href="{{ l.url }}" target="_blank"
    rel="noopener">{{ l.short }}</a>{% endfor %}</div></div>
  <div class="nav">{{ nav }}</div>
</div>

<div class="tiles">
{% for t in tiles %}<div class="tile"><div class="v">{{ t.v }}{% if t.sub %}<span class="vsub" title="{{ t.sub_tip }}">{{ t.sub }}</span>{% endif %}</div><div class="k">{{ t.k }}</div></div>
{% endfor %}</div>

{% if detail_rows %}
<h2>Model details — what we tested</h2>
<div class="card" style="padding:6px 4px"><table>
{% for d in detail_rows %}
<tr><td class="small" style="width:230px;color:var(--muted)">{{ d.k }}</td><td>{{ d.v }}</td></tr>
{% endfor %}
</table></div>
{% endif %}

<h2>Score by category</h2>
<div class="card"><table>
<tr>{% for c in cats %}<th class="num">{{ c.name }}</th>{% endfor %}</tr>
<tr>{% for c in cats %}<td class="num">{{ c.chip }}</td>{% endfor %}</tr>
</table></div>

<h2>Failure &amp; retry assessment <a href="../info.html#fail" class="small" style="font-weight:400">what these mean →</a></h2>
<div class="rollup">
  <span class="pill">raw <b>{{ asmt.raw }}</b></span>
  <span class="pill">attributed <b>{{ asmt.attr }}</b>{% if asmt.excluded %}
    <span class="muted">({{ asmt.excluded }} non-model excluded)</span>{% endif %}</span>
  {% for a in asmt.attr_pills %}<span class="pill"><span class="attr attr-{{ a.cls }}">{{ a.name }}</span> {{ a.n }}</span>{% endfor %}
  <span class="pill">retries <b>{{ asmt.recovered }}</b> recovered · <b>{{ asmt.fatal }}</b> fatal</span>
</div>
{% if asmt.flagged %}
<div class="card"><table>
<tr><th>Task</th><th>Category</th><th>Attribution</th><th>Why — what happened</th>
<th class="num">Score</th><th class="num">Retries</th></tr>
{% for f in asmt.flagged %}
<tr><td class="nowrap"><a href="../tasks/{{ f.task }}.html">{{ f.task }}</a></td>
<td class="small">{{ f.category }}</td>
<td><span class="attr attr-{{ f.cls }}">{{ f.attribution }}</span></td>
<td class="small">{{ f.detail }}</td>
<td class="num">{{ f.score }}</td><td class="num">{{ f.retries }}</td></tr>
{% endfor %}</table></div>
{% else %}
<div class="sub">no failures or retries — every task passed cleanly on the first try.</div>
{% endif %}
<div class="foot" style="margin-top:6px">Attributed score = raw score with
<b>harness</b> (our bugs) and <b>infra</b> (gateway/timeout) failures removed —
it estimates the model's own capability. <b>model</b> failures and
<b>known-limit</b> results still count (they're real signal). Rules and the
excluded set live in <code>directives.yaml</code> · <code>assess:</code>.</div>

<h2>Per-task — aggregated result · click a header to sort</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Task</th><th data-type="text">Category</th><th data-type="num">Score</th>
<th class="num" data-type="num" title="how far this model's score on THIS task moved between repeat runs (population σ). '—' means the task has only been run once, so there is nothing to compare.">σ</th>
<th data-type="text" title="the deciphered reason a non-passing result went the way it did (assess.classify) — attribution + category, full detail on hover">Why</th>
<th class="num" data-type="num">Wall</th>
<th class="num" data-type="num" title="single-shot tasks: first try + any retries after a failure · agentic tasks: turns in the tool-use loop (each turn is a request, not a retry)">Tries / turns</th><th class="num" data-type="num">Tokens in/out</th>
<th data-type="text">From run</th><th>Files</th></tr>
{% for r in task_rows %}
<tr><td class="nowrap"><a href="../tasks/{{ r.id }}.html">{{ r.id }}</a></td>
<td class="small">{{ r.category }}</td><td class="num">{{ r.chip }}</td>
<td class="num small" data-sort="{{ r.sigma_sort }}">{{ r.sigma }}</td>
<td class="small">{{ r.why }}</td>
<td class="num">{{ r.wall }}</td><td class="num" data-sort="{{ r.tries_sort }}">{{ r.tries }}</td>
<td class="num nowrap">{{ r.tokens }}</td>
<td class="small nowrap"><a href="../runs/{{ r.run_id }}.html">{{ r.run_short }}</a>{% if r.nrun_badge %} <span class="nrun" title="{{ r.nrun_title }}">{{ r.nrun_badge }}</span>{% endif %}</td>
<td class="small"><a href="/data/{{ r.run_id }}/{{ slug_q }}/{{ r.id }}/"{% if r.n_runs > 1 %} title="{{ r.nrun_title }}"{% endif %}>open →</a></td></tr>
{% endfor %}</table></div>

{% if verscmp %}
<h2>Version-over-version</h2>
<div class="card">
  <div class="vc-pick">
    <span>compare this model:</span>
    <label>from<select id="vc-a"></select></label>
    <label>to<select id="vc-b"></select></label>
    <span class="vc-note">like-for-like on tasks scored in both versions; edited tests flagged</span>
  </div>
  <div id="vc-out"></div>
</div>
<script type="application/json" id="vc-data">{{ verscmp }}</script>
{{ verscmp_js }}
{% endif %}

{% if runmatrix %}
<h2>Run over run <span class="small muted" style="text-transform:none;letter-spacing:0;font-weight:400">· one row per run (newest first) · columns grouped by category · foot = the aggregate these runs mean into</span></h2>
<div class="mx-scroll"><div class="mx">
  <div class="mx-row head">
    <div class="mx-rail"><span class="rk"></span><span class="nm">Run</span><span class="sc">Avg</span><span class="gp">Cov</span></div>
    <div class="mx-cells">{% for c in runmatrix.cats %}<div class="mx-grp" style="grid-template-columns:repeat({{ c.n }},15px);gap:3px"><span class="mx-clabel" title="{{ c.key }}" style="grid-column:1/-1">{{ c.code }} <span class="cn">{{ c.n }}</span></span></div>{% endfor %}</div>
  </div>
  {% for r in runmatrix.rows %}
  <div class="mx-row">
    <div class="mx-rail"><span class="rk"></span><span class="nm"><a href="../runs/{{ r.run_id }}.html">{{ r.run_short }}</a></span><span class="sc">{{ r.avg }}</span><span class="gp" title="tasks this run covered of the {{ r.cover.split('/')[1] }} this model has data on">{{ r.cover }}</span></div>
    <div class="mx-cells">{% for g in r.groups %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
  {% endfor %}
  <div class="mx-row foot">
    <div class="mx-rail"><span class="fl">aggregate / task →</span></div>
    <div class="mx-cells">{% for g in runmatrix.foot %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
</div></div>
<div class="mxlegend">
  <div class="grp"><span class="k">Score</span><span class="ramp"><i style="--a:.15"></i><i style="--a:.4"></i><i style="--a:.65"></i><i style="--a:.9"></i><i style="--a:1"></i></span><span class="k" style="letter-spacing:0">0 → 1.0</span></div>
  <div class="grp"><span class="sw" style="background:var(--trap)"></span><span class="k">trap</span></div>
  <div class="grp"><span class="sw" style="background:var(--miss)"></span><span class="k">miss</span></div>
  <div class="grp"><span class="sw" style="background:var(--crit)"></span><span class="k">dnf</span></div>
  <div class="grp"><span class="sw na"></span><span class="k">not run</span></div>
</div>
{% endif %}

<h2>Runs featuring this model</h2>
<div class="card"><table>
<tr><th>Run</th><th>Suite</th><th>Tag</th><th class="num">Tasks</th>
<th class="num">Avg score</th><th>Report</th><th>Raw data</th></tr>
{% for r in run_rows %}
<tr><td class="nowrap">{{ r.run_id }}</td><td class="small">v{{ r.suite }}</td>
<td class="small">{{ r.tag }}</td><td class="num">{{ r.n }}</td>
<td class="num">{{ r.avg }}</td>
<td class="small"><a href="../runs/{{ r.run_id }}.html">report →</a></td>
<td class="small"><a href="/data/{{ r.run_id }}/{{ slug_q }}/">browse →</a></td></tr>
{% endfor %}</table></div>

<div class="foot">Aggregates mean every run of a task (partial re-runs
update only what they re-ran). Total time sums wall-clock including every
retry. <b>Tries / turns</b>: a single-shot task shows its one try plus any
retries after a failure; an <b>agentic</b> task shows the number of <b>turns</b>
in its tool-use loop — each turn is a request, not a retry, which is why an
agentic task can show several turns while its retry count is 0. Raw-data links
open the model's transcripts and workspaces on the results server.</div>
{{ sort_js }}
</body></html>"""


def _effort_label(e: dict) -> str:
    """The per-task 'tries' cell, disambiguated by tier: an agentic task's number
    is turns in the tool-use loop (which is why it can read 5 while retries are
    0), a single-shot task's is the first try plus any retries."""
    turns = e.get("turns") or 1
    retries = e.get("n_retries") or 0
    if (e.get("tier") or 1) >= 2:
        lbl = f"{turns} turn" + ("s" if turns != 1 else "")
        return lbl + (f" · {retries} retry" if retries else "")
    if not retries:
        return "1"
    return f"1 + {retries} retr" + ("y" if retries == 1 else "ies")


_LINK_SHORT = {"Hugging Face ↗": "HF ↗"}


def _with_short(links: list[dict]) -> list[dict]:
    for l in links:
        l["short"] = _LINK_SHORT.get(l["label"], l["label"])
    return links


def _model_links(model: str, mo=None, *, local: bool | None = None,
                 publisher: str = "") -> list[dict]:
    """External reference links for a model — Hugging Face for open weights,
    OpenRouter for gateway-served ones.

    The exact repo/slug lives only in the model yaml, which the public build does
    NOT ship (the yamls carry private endpoints). So the yaml, when present, gives
    a DIRECT link; without it we fall back to a search built from the report's own
    model name and the publisher recorded in the run data — both of which always
    ship. The links therefore widen from a direct hit to a search in the public
    build rather than disappearing, which is what happened when this depended on
    the yaml alone. `short` is the compact header form; `label` the long one.
    """
    from urllib.parse import quote

    if not isinstance(model, str):
        mo, model = model, getattr(model, "name", "")

    if mo and mo.model:
        mid = mo.model
        is_local = bool(mo.local)
        base = (mo.base_url or "").lower()
        is_claude = "anthropic" in base or mo.provider == "claude-cli"
    else:
        mid, base = "", ""
        is_local = bool(local)
        is_claude = "claude" in model.lower() or "anthropic" in model.lower()

    if is_claude:
        return _with_short([{
            "label": "Anthropic ↗",
            "url": "https://docs.anthropic.com/en/docs/about-claude/models"}])

    name = mid.split("/")[-1] if mid else model
    hf_search = f"https://huggingface.co/models?search={quote(name)}"
    or_search = f"https://openrouter.ai/models?q={quote(name)}"
    hf = {"label": "Hugging Face ↗", "url": hf_search}
    orr = {"label": "OpenRouter ↗", "url": or_search}

    if mid and is_local and mid.count("/") == 1 and " " not in mid:
        hf["url"] = f"https://huggingface.co/{mid}"
    elif not mid and publisher and " " not in publisher:
        hf["url"] = f"https://huggingface.co/{publisher}/{name}"
    if mid and not is_local and "openrouter" in base and mid.count("/") >= 1:
        orr["url"] = f"https://openrouter.ai/{mid}"

    return _with_short([hf, orr] if is_local else [orr, hf])


def _model_detail_rows(mo, mi: dict, fp, hosts: list) -> list[dict]:
    """(label, value) rows describing the exact model as tested — id, quant, max
    context, arch, VRAM, the generation budget it ran under, price, gateway host."""
    rows = []
    add = lambda k, v: rows.append({"k": k, "v": v})
    if mo:
        add("Model id", html.escape(mo.model))
        add("Runs as", "local · LM Studio (OpenAI-compatible API)" if mo.local
            else f"hosted · {html.escape(mo.provider)}")
    quant = mi.get("quantization") or (fp or {}).get("quant")
    if quant:
        add("Quantization", html.escape(str(quant)))
    ctx = mi.get("max_context_length") or (fp or {}).get("native_ctx")
    if ctx:
        add("Max context", f"{ctx:,} tokens")
    if mi.get("arch"):
        add("Architecture", html.escape(str(mi["arch"])))
    if mi.get("publisher"):
        add("Publisher", html.escape(str(mi["publisher"])))
    if fp:
        add("Weights on disk", f"{fp['weights_gb']:.1f} GB")
        total = (fp["weights_gb"] + fp["kv_fixed_gb"]
                 + fp["kv_per_tok_gb"] * VRAM_REF_CTX)
        add(f"VRAM to run @{VRAM_REF_CTX // 1024}k",
            f"{total:.0f} GB (weights + KV cache)")
    if mo:
        add("Generation budget (as tested)",
            f"{mo.max_tokens:,} max tokens · temperature {mo.temperature}")
        if not mo.local:
            p = mo.pricing or {}
            if p.get("input_per_mtok") or p.get("output_per_mtok"):
                add("List price", f"${p.get('input_per_mtok', 0)}/M tok in · "
                    f"${p.get('output_per_mtok', 0)}/M tok out")
    if hosts:
        add("Served by (gateway host)", html.escape(", ".join(hosts)))
    return rows


def _cat_code(tids: list[str]) -> str:
    """Short matrix column-header code for a category = its shared task-id prefix
    (ag, py, ctx, web, rs, if, hl, math, ext, tool), uppercased. Keeps the header
    from overflowing a narrow 2-task column group the way the full name does; the
    full category name rides in the cell's title."""
    return tids[0].split("-")[0].upper() if tids else ""


def _mx_cell(entry, tdef, acfg, suspect, href):
    """One model×task matrix cell — fill = score ramp, colour = failure TYPE
    (assess.classify), so the shade never disagrees with the diagnosis. Shared by
    the overview, the model page's run-matrix, and the discriminate hard-matrix.
    `href` is where the cell links; tips are keyed off the task id."""
    from . import assess as _assess
    tid = tdef.id
    if entry is None:
        return {"cls": "na", "a": "0", "tip": f"{tid} · not run", "href": href}
    cat = _assess.classify(entry, tdef, acfg, suspect)["category"]
    sc = entry.get("score") or {}
    val = sc.get("score")
    if cat == "fell-for-trap":
        return {"cls": "trap", "a": "0", "tip": f"{tid} · fell-for-trap", "href": href}
    if cat == "retrieval-miss":
        return {"cls": "miss", "a": "0", "tip": f"{tid} · retrieval-miss", "href": href}
    if cat in ("rumination-spiral", "incomplete-output",
               "agentic-max-turns", "infinite-loop"):
        return {"cls": "dnf", "a": "0", "tip": f"{tid} · {cat}", "href": href}
    if sc.get("status") == "scored" and val is not None:
        v = max(0.0, min(1.0, val))
        return {"cls": "pass", "a": f"{0.10 + 0.90 * v:.3f}",
                "tip": f"{tid} · {val:.2f}", "href": href}
    return {"cls": "na", "a": "0", "tip": f"{tid} · {cat}", "href": href}


def build_model_report(model: str, runs: list[dict], tdefs: dict,
                       dataset_label: str = "",
                       versions: list[tuple] | None = None) -> str:
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    mine = [(tid, info["agg"][model]) for tid, info in task_data.items()
            if model in info["agg"]]
    entries = [e for _, e in mine]
    s = _summarize(entries)
    where = "local" if s["local"] else "cloud / CLI"
    if s.get("quant"):
        where += f" · {s['quant']}"
    if s.get("hosts"):
        where += " · via " + (s["hosts"][0] if len(s["hosts"]) == 1
                              else f"{len(s['hosts'])} hosts")
    my_runs = [r for r in runs if any(res["model"] == model
                                      for res in r["results"])]
    graded = [e for e in entries if e["score"].get("status") == "scored"]
    npass = sum(1 for e in graded if e["score"]["score"] >= 0.8)

    from . import assess
    acfg = assess.load_cfg()
    suspect = assess.suspect_answers(task_data, tdefs, acfg)
    am = assess.assess_model(model, task_data, tdefs, acfg, suspect)
    _ATTR_NAMES = {"model": "model", "harness": "harness", "infra": "infra",
                   "known-limit": "limit", "clean": "clean"}
    asmt = {
        "raw": f"{am['raw_score']:.3f}" if am["raw_score"] is not None else "—",
        "attr": (f"{am['attributed_score']:.3f}"
                 if am["attributed_score"] is not None else "—"),
        "excluded": am["excluded"],
        "recovered": am["retries"]["recovered"], "fatal": am["retries"]["fatal"],
        "attr_pills": [{"cls": a, "name": _ATTR_NAMES.get(a, a), "n": n}
                       for a, n in sorted(am["by_attribution"].items(),
                                          key=lambda kv: -kv[1])],
        "flagged": [{**f, "cls": f["attribution"],
                     "score": (f"{f['score']:.3f}" if f["score"] is not None
                               else "—")}
                    for f in am["flagged"]],
    }

    attr_disp = (f"{am['attributed_score']:.3f}"
                 if am["attributed_score"] is not None else "—")
    _ci = s.get("score_ci95")
    tiles = [
        {"v": s["chip"] if s["avg_score_val"] is None else
         f"{s['avg_score_val']:.3f}", "k": "raw score",
         "sub": ("" if _ci is None else "±" + f"{_ci:.3f}".lstrip("0")),
         "sub_tip": "95% confidence band across tasks (±1.96·SE)"},
        {"v": attr_disp, "k": "attributed score"},
        {"v": f"{npass}/{len(graded)}", "k": "tasks ≥ 0.80"},
        {"v": s["att_per_pass"], "k": "tries / pass (lower=better)"},
        {"v": fmt_span(s["wall_ms_sum"]), "k": "total time"},
        {"v": s["tps"], "k": "gen tok/s"},
        {"v": s["cost"], "k": "cost / run"},
        {"v": s["first_try"], "k": "first-try clean"},
    ]
    try:
        from .registry import get_model
        mo = get_model(model)
    except Exception:
        mo = None
    newest_e = max(entries, key=lambda e: e.get("started") or "") if entries else {}
    meta_info = (newest_e.get("model_meta") or {}).get("model_info") or {}
    hosts = sorted({h for e in entries for h in (e.get("served_by") or [])})
    fp = None
    if mo and mo.local:
        try:
            from . import gguf
            fp = gguf.footprint(mo.model)
        except Exception:
            fp = None
    if fp:
        total = (fp["weights_gb"] + fp["kv_fixed_gb"]
                 + fp["kv_per_tok_gb"] * VRAM_REF_CTX)
        tiles.append({"v": f"{total:.0f} GB",
                      "k": f"VRAM @{VRAM_REF_CTX // 1024}k · "
                           f"{fp['weights_gb']:.0f}GB wt + KV · {fp['quant']}"})
    detail_rows = _model_detail_rows(mo, meta_info, fp, hosts)
    model_links = _model_links(model, mo, local=s["local"],
                               publisher=meta_info.get("publisher", ""))

    all_cats = sorted({tdefs[tid].category for tid, _ in mine})
    cats = []
    for cat in all_cats:
        sc = [e["score"]["score"] for tid, e in mine
              if tdefs[tid].category == cat
              and e["score"].get("status") == "scored"]
        cats.append({"name": cat, "chip": _score_cell(_avg(sc))})

    task_rows = []
    for tid, e in sorted(mine):
        ti = e["tokens_in"] or 0
        to = e["tokens_out"] or 0
        task_rows.append({
            "id": tid, "category": e["category"],
            "chip": score_chip(e["score"]),
            "why": why_cell(diagnose(e, tdefs.get(tid), acfg, suspect)),
            "wall": fmt_ms(e["wall_ms"]),
            "tries": _effort_label(e),
            "tries_sort": (e.get("turns") or 1) if (e.get("tier") or 1) >= 2
                          else (e.get("n_attempts") or 1),
            "tokens": f"{ti:,} / {to:,}" if (ti or to) else "—",
            "run_id": e["run_id"], "run_short": e["run_id"].split("_")[0],
            "sigma": (f"±{e['score_sigma']:.3f}"
                      if e.get("n_runs", 1) > 1
                      and e.get("score_sigma") is not None else "—"),
            "sigma_sort": (f"{e['score_sigma']:.6f}"
                           if e.get("n_runs", 1) > 1
                           and e.get("score_sigma") is not None else ""),
            "n_runs": e.get("n_runs", 1),
            "n_scored": e.get("n_scored", e.get("n_runs", 1)),
            "runs_title": ", ".join(e.get("run_ids") or [e["run_id"]]),
            "nrun_badge": _runs_badge(e.get("n_runs", 1),
                                      e.get("n_scored", e.get("n_runs", 1)),
                                      e.get("run_ids") or [e["run_id"]])[0],
            "nrun_title": _runs_badge(e.get("n_runs", 1),
                                      e.get("n_scored", e.get("n_runs", 1)),
                                      e.get("run_ids") or [e["run_id"]])[1],
        })

    run_rows = []
    for r in reversed(my_runs):
        res = [x for x in r["results"] if x["model"] == model]
        avg = _avg([x["score"]["score"] for x in res
                    if x["score"].get("status") == "scored"])
        run_rows.append({
            "run_id": r["run_id"], "suite": r["manifest"].get("suite_version", "?"),
            "tag": r["manifest"].get("tag", ""), "n": len(res),
            "avg": f"{avg:.3f}" if avg is not None else "—",
        })

    rm_cat_tids: dict[str, list[str]] = {}
    for tid, _ in mine:
        rm_cat_tids.setdefault(tdefs[tid].category, []).append(tid)
    for c in rm_cat_tids:
        rm_cat_tids[c].sort()
    rm_cats = [c for c in all_cats if rm_cat_tids.get(c)]
    per_run: dict[str, dict[str, dict]] = {}
    for tid, info in task_data.items():
        for e in info["history"]:
            if e["model"] == model:
                per_run.setdefault(e["run_id"], {})[tid] = e

    def _runcell(entry, tid, run_id):
        href = (f"../runs/{run_id}.html" if run_id
                else f"../tasks/{tid}.html#m-{_slug_name(model)}")
        return _mx_cell(entry, tdefs[tid], acfg, suspect, href)

    rm_rows = []
    for r in reversed(my_runs):
        rid = r["run_id"]
        cells = per_run.get(rid, {})
        res = [x for x in r["results"] if x["model"] == model]
        avg = _avg([x["score"]["score"] for x in res
                    if x["score"].get("status") == "scored"])
        ncov = sum(1 for tid, _ in mine if tid in cells)
        rm_rows.append({
            "run_short": rid.split("_")[0], "run_id": rid,
            "avg": f"{avg:.3f}" if avg is not None else "—",
            "cover": f"{ncov}/{len(mine)}",
            "groups": [[_runcell(cells.get(tid), tid, rid)
                        for tid in rm_cat_tids[c]] for c in rm_cats],
        })
    rm_foot = [[_runcell(task_data[tid]["agg"].get(model), tid, None)
                for tid in rm_cat_tids[c]] for c in rm_cats]
    runmatrix = ({"cats": [{"key": c, "code": _cat_code(rm_cat_tids[c]), "n": len(rm_cat_tids[c])} for c in rm_cats],
                  "rows": rm_rows, "foot": rm_foot}
                 if (rm_rows and rm_cats) else None)

    verscmp = ""
    if versions:
        payload = model_version_payload(model, versions)
        if len(payload["versions"]) >= 2 and payload["pairs"]:
            import json as _json
            verscmp = _json.dumps(payload).replace("</", "<\\/")
    return _env.from_string(MODEL_TEMPLATE).render(
        nav=_nav("../"),
        sort_js=_SORT_JS, verscmp=verscmp, verscmp_js=_VERSCMP_JS,
        css=BASE_CSS, model=html.escape(model), slug_q=quote(model),
        where=where, dataset_label=dataset_label, n_runs=len(my_runs),
        tiles=tiles, cats=cats, task_rows=task_rows, run_rows=run_rows,
        runmatrix=runmatrix,
        detail_rows=detail_rows, model_links=model_links, asmt=asmt)


def build_index(runs: list[dict], tasks_dir: Path | None = None,
                dataset_label: str = "", dataset_key: str = "live",
                versions: list[tuple] | None = None) -> str:
    run_ids = [r["run_id"] for r in runs]
    color_overrides, hidden = _model_prefs()
    all_models = sorted({res["model"] for r in runs for res in r["results"]}
                        - hidden)

    tdefs = _task_defs(tasks_dir)
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    all_cats = sorted({tdefs[tid].category for tid in task_data})

    tiles = [
        {"v": f"v{config.suite_version()}" if not dataset_label
         else dataset_label.split()[-1], "k": "test suite"},
        {"v": str(len(runs)), "k": "runs"},
        {"v": str(len(all_models)), "k": "models tracked"},
        {"v": str(len(task_data)) or str(len(tdefs)), "k": "tasks with data"},
        {"v": (runs[-1]["run_id"].split("_")[0] if runs else "—"), "k": "latest run"},
    ]

    first_seen: list[str] = []
    for r in runs:
        for res in r["results"]:
            if res["model"] not in first_seen and res["model"] not in hidden:
                first_seen.append(res["model"])
    try:
        vranks = version_rankings(versions)
    except Exception:
        vranks = []
    color_order = list(first_seen)
    for v in vranks:
        for m in v["ranks"]:
            if m not in color_order and m not in hidden:
                color_order.append(m)
    from .registry import infer_family, load_families, load_models
    _reg = {mo.name: mo for mo in load_models(include_disabled=True)}
    fam_of = {m: (_reg[m].family_name if m in _reg else infer_family(m))
              for m in color_order}
    slot = _model_colors(color_order, color_overrides, fam_of, load_families())
    legend = [{"model": m, "color": slot[m]} for m in first_seen]
    legend_html = chart_legend(legend)


    by_model: dict[str, list[dict]] = {}
    for info in task_data.values():
        for m, e in info["agg"].items():
            by_model.setdefault(m, []).append(e)

    cat_rows = []
    for m in all_models:
        cells = []
        for cat in all_cats:
            scored = [e["score"]["score"] for e in by_model.get(m, [])
                      if e["category"] == cat
                      and e["score"].get("status") == "scored"]
            avg = _avg(scored)
            cells.append({"html": _score_cell(avg),
                          "sort": "" if avg is None else f"{avg:.6f}"})
        cat_rows.append({"model": _mlink(m), "model_sort": m, "cells": cells})

    bump = bump_chart(vranks, slot) if len(vranks) >= 2 else ""

    from .fit import task_fit

    def _is_local(m: str) -> bool:
        for e in by_model.get(m, []):
            lo = (e.get("model_meta") or {}).get("local")
            if lo is not None:
                return bool(lo)
        return False

    local_models = [m for m in all_models if _is_local(m)]
    remote_models = [m for m in all_models if not _is_local(m)]

    summaries = {m: {"model": m, **_summarize(by_model.get(m, []))}
                 for m in all_models}

    _ids = _model_ids()
    _free_tier = {m for m in all_models
                  if str(_ids.get(m, "")).endswith(":free")}

    def _fit_rows_for(subset: list[str]):
        """One ACTIONABLE line per category instead of a wall of names.

        Listing 35 "top" models is not a recommendation, and when the whole
        field ties at 1.00 a score ranking is arbitrary — so the picks are
        tie-aware: among everything that clears the capable bar, name the
        cheapest and the fastest (the axes that actually decide it), show how
        many tie at the top, and collapse the rest behind a disclosure."""
        fr = task_fit({m: by_model.get(m, []) for m in subset}, all_cats)
        rows = []
        for row in fr["rows"]:
            cls = row["classes"]
            ok = {m: sc[1] for m, sc in cls.items()
                  if sc[0] in ("excellent", "capable")}
            bad = [(m, sc[1]) for m, sc in cls.items()
                   if sc[0] in ("weak", "avoid")]
            bad.sort(key=lambda x: x[1])
            best_v = max(ok.values()) if ok else None
            tied = [m for m, v in ok.items() if best_v is not None
                    and abs(v - best_v) < 1e-9]

            def _pick(cands, key, reverse=False):
                """Cheapest/fastest among the capable — tie-broken by SCORE, so a
                pack of $0 models (free APIs + locals billed as electricity)
                yields the best of them rather than an arbitrary one."""
                vals = [(m, summaries[m].get(key)) for m in cands
                        if summaries[m].get(key) is not None]
                if not vals:
                    return None
                return sorted(vals, key=lambda x: ((-x[1] if reverse else x[1]),
                                                   -cands[x[0]]))[0]

            durable = {m: v for m, v in ok.items() if m not in _free_tier}
            cheap = _pick(durable, "cost_val")
            freebie = _pick({m: v for m, v in ok.items() if m in _free_tier},
                            "cost_val")
            fast = _pick(ok, "tps_val", reverse=True)

            def _tag(m):
                if m in _free_tier:
                    return (" <a href='info.html#freetier' class='muted'"
                            " title='promotional free variant on OpenRouter"
                            " (:free) — the price is expected to change; not a"
                            " durable cost. Click for the full explanation.'>"
                            "⏳ free-tier</a>")
                return " ⚡" if summaries[m].get("local") else ""

            def _cell(pick, unit):
                if not pick:
                    return "—"
                m, v = pick
                num = (fmt_cost(v) if unit == "$" else f"{v:,.0f} tok/s")
                return f"{_mlink(m)} <span class='muted'>{num}</span>{_tag(m)}"

            rows.append({
                "category": row["category"],
                "n_ok": len(ok), "n_total": len(cls),
                "best": (f"{_mlink(tied[0])} <span class='muted'>{best_v:.2f}</span>"
                         + (f" <span class='muted'>({len(tied)} tied)</span>"
                            if len(tied) > 1 else "")) if tied else "—",
                "cheap": _cell(cheap, "$"),
                "freebie": (f"{_mlink(freebie[0])}{_tag(freebie[0])}"
                            if freebie else ""),
                "fast": _cell(fast, "tok/s"),
                "n_bad": len(bad),
                "avoid": ", ".join(f"{_mlink(m)} ({v:.2f})" for m, v in bad[:3]) or "—",
                "avoid_all": ", ".join(f"{_mlink(m)} ({v:.2f})" for m, v in bad[3:]),
            })
        return fr, rows

    fitres, fit_rows = _fit_rows_for(all_models)
    _, fit_local = _fit_rows_for(local_models)
    _, fit_remote = _fit_rows_for(remote_models)

    tps_max = max(((s["tps_val"] or 0) for s in summaries.values()),
                  default=0) or 1
    speed_rows = []
    for m in all_models:
        s = summaries[m]
        where = "local" if s["local"] else "cloud / CLI"
        if s.get("quant"):
            where += f" · {s['quant']}"
        if s.get("hosts"):
            where += " · via " + (s["hosts"][0] if len(s["hosts"]) == 1
                                  else f"{len(s['hosts'])} hosts")
        speed_rows.append({
            "model": _mlink(m), "tps": s["tps"],
            "tps_bar": bar(s["tps_val"] or 0, tps_max),
            "prefill": s["prefill"],
            "ttft": s["ttft"], "tokens": f"{s['tokens_total']:,}",
            "cost": s["cost"] + (" ✓" if s.get("billed") else ""),
            "cold": s["cold"],
            "vram": s["vram"], "watts": s["watts"], "energy": s["energy"],
            "energy_cost": s["energy_cost"],
            "where": where,
        })

    value_rows = []
    for m in all_models:
        s = summaries[m]
        value_rows.append({
            "model": _mlink(m), "first_try": s["first_try"],
            "app": s["att_per_pass"],
            "spm": s["score_per_min"], "spd": s["score_per_dollar"],
            "p50": s["p50"], "p95": s["p95"],
            **_consistency(m, task_data),
        })

    n_suite = len(tdefs) or 1
    ranked = sorted(all_models, key=_leader_key(summaries))
    complete = [m for m in ranked if len(by_model.get(m, [])) >= n_suite]
    incomplete = [m for m in ranked if len(by_model.get(m, [])) < n_suite]
    mids = _model_ids()
    podium = []
    for m in complete + incomplete:
        s = summaries[m]
        n = len(by_model.get(m, []))
        podium.append({
            "model": m, "slug": _slug_name(m),
            "model_id": mids.get(m, ""),
            "score": (_fmt_score(s["avg_score_val"])
                      if s["avg_score_val"] is not None else "—"),
            "ci": ("" if s.get("score_ci95") is None
                   else "±" + f"{s['score_ci95']:.3f}".lstrip("0")),
            "app": s["att_per_pass"], "app_ctx": s["app_ctx"],
            "tps": s["tps"], "cost": s["cost"],
            "where": "local" if s["local"] else "cloud / CLI",
            "total_time": fmt_span(s["wall_ms_sum"]),
            "coverage": f"{n}/{n_suite}",
            "partial": n < n_suite,
        })

    from . import gguf
    from .registry import load_models as _load_models
    _reg = {mo.name: mo for mo in _load_models(include_disabled=True)}
    _fp_cache: dict[str, dict | None] = {}

    def _footprint(name):
        mo = _reg.get(name)
        if not mo or not mo.local:
            return None
        if mo.model not in _fp_cache:
            try:
                _fp_cache[mo.model] = gguf.footprint(mo.model)
            except Exception:
                _fp_cache[mo.model] = None
        return _fp_cache[mo.model]

    def _standing(m, rank, cov):
        s = summaries[m]
        fp = _footprint(m)
        return {
            "rank": rank, "kind": "local" if s["local"] else "remote",
            "model": _mlink(m), "model_sort": m,
            "where": "local ⚡" if s["local"] else "API / CLI",
            "score": (f"{s['avg_score_val']:.3f}"
                      if s["avg_score_val"] is not None else "—"),
            "score_v": f"{s['avg_score_val'] or 0:.4f}",
            "low": (f"{s['lowest_val']:.3f}" if s.get("lowest_val") is not None
                    else "—"),
            "low_v": f"{s['lowest_val'] if s.get('lowest_val') is not None else 1:.4f}",
            "low_task": s.get("lowest_task", ""),
            "cov": cov, "tps": s["tps"], "tps_v": f"{s['tps_val'] or 0:.2f}",
            "cost": s["cost"], "value": s["score_per_dollar"],
            "size_disp": (f"{fp['weights_gb']:.1f} GB · {fp['quant']}"
                          if fp else "—"),
            "w_v": (fp["weights_gb"] if fp else 0),
            "kvtok": (f"{fp['kv_per_tok_gb']:.9f}" if fp else "0"),
            "kvfixed": (f"{fp['kv_fixed_gb']:.4f}" if fp else "0"),
            "native": (fp["native_ctx"] if fp else 0),
            "pure_v": f"{s['avg_score_val'] or 0:.4f}",
            "value_v": (f"{s['score_per_dollar_val']:.4f}"
                        if s.get("score_per_dollar_val") is not None else ""),
            "speed_v": (f"{s['score_per_min_val']:.4f}"
                        if s.get("score_per_min_val") is not None else ""),
            "firsttry_v": (f"{s['first_try_val']:.4f}"
                           if s.get("first_try_val") is not None else ""),
            "eff_v": f"{(s['avg_score_val'] or 0) + (0 if m in dominated else 10):.4f}",
            "hard_v": (f"{hard_mean[m]:.4f}" if m in hard_mean else ""),
            "easy_v": (f"{easy_mean[m]:.4f}" if m in easy_mean else ""),
        }

    _dstats = discrimination_stats(runs, tdefs)
    hard_mean = {h["model"]: h["mean"] for h in _dstats["hard_rank"]}
    easy_mean = {h["model"]: h["mean"] for h in _dstats["easy_rank"]}
    _eff = [{"m": m, "s": summaries[m]["avg_score_val"] or 0,
             "c": summaries[m]["cost_val"] or 0, "t": summaries[m]["tps_val"] or 0}
            for m in complete]
    dominated = {p["m"] for p in _eff if any(
        q is not p and q["s"] >= p["s"] and q["c"] <= p["c"] and q["t"] >= p["t"]
        and (q["s"] > p["s"] or q["c"] < p["c"] or q["t"] > p["t"]) for q in _eff)}

    standings = [_standing(m, str(i + 1),
                           f"{len(by_model.get(m, []))}/{n_suite}")
                 for i, m in enumerate(complete)]
    standings += [_standing(m, "—",
                            f"{len(by_model.get(m, []))}/{n_suite} partial")
                  for m in incomplete]

    points = []
    for m in all_models:
        graded = [e for e in by_model.get(m, [])
                  if e["score"].get("status") == "scored" and e["tokens_out"]]
        if graded:
            points.append({
                "x": sum(e["tokens_out"] for e in graded) / len(graded),
                "y": sum(e["score"]["score"] for e in graded) / len(graded),
                "label": m,
                "color": slot.get(m, "var(--accent)"),
            })
    frontier = scatter(sorted(points, key=lambda p: p["x"]))

    def _vpt(m, x, xdisp):
        s = summaries[m]
        return {"x": x, "y": s["avg_score_val"], "label": m,
                "color": slot.get(m, "var(--accent)"),
                "tip": f'{m} · {s["avg_score_val"]:.3f} · {xdisp}'}

    cost_pts, spd = [], {"all": [], "local": [], "remote": []}
    for m in complete:
        s = summaries[m]
        if s["avg_score_val"] is None:
            continue
        coh = "local" if s["local"] else "remote"
        if s.get("tps_val"):
            p = _vpt(m, s["tps_val"], f'{s["tps_val"]:.0f} tok/s')
            spd["all"].append(p); spd[coh].append(p)
        if not s["local"] and s.get("api_cost_val"):
            cost_pts.append(_vpt(m, s["api_cost_val"], s["cost"]))
    cost_scatter = pareto_scatter(
        cost_pts, "cost to run the full suite (USD) — cheaper is left; "
        "dashed = best score per dollar", x_minimize=True, x_fmt="${:,.0f}")
    speed_scatter = {k: pareto_scatter(
        v, "generation speed (tok/s) — faster is right; dashed = best score "
        "per tok/s", x_minimize=False, x_fmt="{:,.0f}") for k, v in spd.items()}

    task_rows = []
    for tid, info in sorted(task_data.items()):
        tdef = tdefs[tid]
        scored = {m: e["score"]["score"] for m, e in info["agg"].items()
                  if e["score"].get("status") == "scored"}
        vals = list(scored.values())
        n = len(vals)
        aced = sum(1 for v in vals if v >= 0.999)
        spread = (max(vals) - min(vals)) if n >= 2 else 0.0
        task_rows.append({
            "id": tid,
            "title": html.escape(tdef.title),
            "category": tdef.category, "tier": tdef.tier,
            "scoring": tdef.scoring_type,
            "n_models": len(info["agg"]),
            "aced": f"{aced}/{n}" if n else "—",
            "aced_frac": f"{(aced / n) if n else 0:.4f}",
            "spread": f"{spread:.2f}" if n >= 2 else "—",
            "spread_v": f"{spread:.4f}",
            "hardened": tid in config.HARDENED_TASKS,
        })

    runs_view = []
    for r in reversed(runs):
        pending = sum(1 for res in r["results"]
                      if res["score"].get("status") == "pending")
        runs_view.append({**r, "pending": pending})

    from . import assess as _assess
    _acfg = _assess.load_cfg()
    _suspect = _assess.suspect_answers(task_data, tdefs, _acfg)
    _pass_th = _acfg.get("pass_threshold", 0.8)
    _cat_tids: dict[str, list[str]] = {}
    for _tid in task_data:
        _cat_tids.setdefault(tdefs[_tid].category, []).append(_tid)
    for _c in _cat_tids:
        _cat_tids[_c].sort()
    _live_cats = [c for c in all_cats if _cat_tids.get(c)]

    def _mcell(entry, tdef, model=None):
        href = f"tasks/{tdef.id}.html" + (f"#m-{_slug_name(model)}" if model else "")
        return _mx_cell(entry, tdef, _acfg, _suspect, href)

    _mrank = sorted(all_models, key=lambda m: (
        -(summaries[m]["avg_score_val"]
          if summaries[m]["avg_score_val"] is not None else -1.0), m))
    _lead_v = next((summaries[m]["avg_score_val"] for m in _mrank
                    if summaries[m]["avg_score_val"] is not None), None)
    _lead_m = next((m for m in _mrank
                    if summaries[m]["avg_score_val"] is not None), None)
    _lead_ci = summaries[_lead_m]["score_ci95"] if _lead_m else None
    _flag_of = {r["tid"]: r["flag"] for r in _dstats["rows"]}
    _sub_of = {tid: ("hard" if _flag_of.get(tid) in ("frontier", "discriminator")
                     else "easy" if _flag_of.get(tid) in ("ceiling", "dead")
                     else "mid") for tid in task_data}
    _hard_ids = [t for t, s in _sub_of.items() if s == "hard"]
    _easy_ids = [t for t, s in _sub_of.items() if s == "easy"]

    def _sub_mean(model, ids):
        xs = [e["score"]["score"] for tid in ids
              if (e := task_data[tid]["agg"].get(model))
              and e["score"].get("status") == "scored"
              and e["score"].get("score") is not None]
        return sum(xs) / len(xs) if xs else None

    matrix_rows = []
    for i, m in enumerate(_mrank):
        agg = summaries[m]["avg_score_val"]
        groups = [[{**_mcell(task_data[tid]["agg"].get(m), tdefs[tid], m),
                    "sub": _sub_of[tid]}
                   for tid in _cat_tids[c]] for c in _live_cats]
        ci = summaries[m]["score_ci95"]
        if agg is None:
            score_s, gap_s, ci_s, tied = "—", "", "", False
        else:
            score_s = f"{agg:.3f}"
            gap_s = ("—" if (i == 0 or _lead_v is None
                             or abs(agg - _lead_v) < 1e-9)
                     else "+" + f"{_lead_v - agg:.3f}".lstrip("0"))
            ci_s = "" if ci is None else "±" + f"{ci:.3f}".lstrip("0")
            tied = (i != 0 and _lead_v is not None and ci is not None
                    and _lead_ci is not None
                    and (agg + ci) >= (_lead_v - _lead_ci))
        _mh, _me = _sub_mean(m, _hard_ids), _sub_mean(m, _easy_ids)
        matrix_rows.append({
            "rank": i + 1, "model": _mlink(m), "score": score_s,
            "ci": ci_s, "tied": tied,
            "gap": gap_s, "lead": (i == 0 and agg is not None),
            "m_all": ("" if agg is None else f"{agg:.6f}"),
            "m_hard": ("" if _mh is None else f"{_mh:.6f}"),
            "m_easy": ("" if _me is None else f"{_me:.6f}"),
            "groups": groups})

    matrix_foot = []
    for c in _live_cats:
        grp = []
        for tid in _cat_tids[c]:
            vals = [e["score"]["score"] for e in task_data[tid]["agg"].values()
                    if e["score"].get("status") == "scored"
                    and e["score"].get("score") is not None]
            if vals:
                v = sum(vals) / len(vals)
                grp.append({"cls": "pass", "sub": _sub_of[tid],
                            "a": f"{0.10 + 0.90 * max(0.0, min(1.0, v)):.3f}",
                            "tip": f"{tid} · fleet avg {v:.2f}",
                            "href": f"tasks/{tid}.html"})
            else:
                grp.append({"cls": "na", "a": "0", "sub": _sub_of[tid],
                            "tip": f"{tid} · no data",
                            "href": f"tasks/{tid}.html"})
        matrix_foot.append(grp)

    matrix = ({"cats": [{"key": c, "code": _cat_code(_cat_tids[c]), "n": len(_cat_tids[c])} for c in _live_cats],
               "rows": matrix_rows, "foot": matrix_foot,
               "n_hard": len(_hard_ids), "n_easy": len(_easy_ids),
               "n_all": len(task_data)}
              if (matrix_rows and _live_cats) else None)

    mast_eyebrow = [
        dataset_label or f"Suite v{config.suite_version()}",
        f"{len(task_data)} tasks", f"{len(all_models)} models",
        (f"latest {runs[-1]['run_id'].split('_')[0]}" if runs else "no runs yet"),
    ]
    _aggs = [summaries[m]["avg_score_val"] for m in all_models
             if summaries[m]["avg_score_val"] is not None]
    _fleet = sum(_aggs) / len(_aggs) if _aggs else None
    _below = _tot = 0
    for _info in task_data.values():
        for _e in _info["agg"].values():
            _s = _e["score"]
            if _s.get("status") == "scored" and _s.get("score") is not None:
                _tot += 1
                if _s["score"] < _pass_th:
                    _below += 1
    mast_stats = []
    if _fleet is not None:
        _lead_m = _mrank[0]
        mast_stats.append({"n": f"{_fleet:.3f}", "k": "Fleet score",
                           "d": "mean of ranked models", "up": True})
        mast_stats.append({"n": f"{summaries[_lead_m]['avg_score_val']:.3f}",
                           "k": "Leader", "d": _lead_m})
        _fast_v, _fast_m = max(((summaries[m]["tps_val"] or 0, m)
                                for m in all_models), default=(0, None))
        if _fast_m and _fast_v:
            mast_stats.append({"n": f"{_fast_v:.0f}<small>tok/s</small>",
                               "k": "Fastest pace", "d": _fast_m})
        if _tot:
            mast_stats.append({"n": f"{100 * _below / _tot:.1f}<small>%</small>",
                               "k": "Sub-pass cells",
                               "d": f"score &lt; {_pass_th:g}",
                               "warn": _below / _tot > 0.15})
    else:
        mast_stats.append({"n": "—", "k": "No runs yet",
                           "d": "run the suite to populate"})

    return _env.from_string(INDEX_TEMPLATE).render(
        nav=_nav(""), public_nav=_PUBLIC_NAV,
        sort_js=_SORT_JS,
        css=BASE_CSS, tiles=tiles, runs=runs_view, run_ids=run_ids,
        mast_eyebrow=mast_eyebrow, mast_stats=mast_stats, matrix=matrix,
        podium=podium, standings=standings, task_rows=task_rows,
        frontier=frontier, bump=bump,
        cost_scatter=cost_scatter, speed_scatter=speed_scatter,
        scatter_js=_SCATTER_HOVER_JS, legend_html=legend_html,
        value_rows=value_rows, dataset_label=dataset_label,
        dataset_key=dataset_key, dataset_caveat=_pre_v05_caveat(dataset_key),
        suite_version=config.suite_version(),
        data_asof=(runs[-1]["run_id"].split("_")[0] if runs else ""),
        categories=all_cats, cat_rows=cat_rows,
        fit_rows=fit_rows, fit_local=fit_local, fit_remote=fit_remote,
        fit_note=fitres["directives"].get("note", ""),
        fit_th=fitres["directives"]["thresholds"],
        fit_vp=fitres["directives"]["value_pick"],
        speed_rows=speed_rows)



def _changelog_for_version(md: str, version: str) -> str:
    """Trim CHANGELOG.md to the CURRENT dataset's major.minor. Live reports show
    exactly one dataset, so an end user on v0.6 has no use for the v0.5 / v0.4
    history — those live in their own archived reports. Keeps the preamble and
    `## Unreleased`, keeps every `## <major.minor>.x` section, drops older minors."""
    mm = ".".join(version.split(".")[:2])
    out, keep = [], True
    for ln in md.splitlines():
        m = re.match(r"^##\s+(\S+)", ln)
        if m:
            tok = m.group(1)
            keep = (tok.lower() == "unreleased" or tok == mm
                    or tok.startswith(mm + "."))
        if keep:
            out.append(ln)
    return "\n".join(out).rstrip() + "\n"


def _md_to_html(md: str) -> str:
    """Minimal markdown -> HTML for CHANGELOG.md. Deliberately tiny — we author
    the file, so we control the subset and need no third-party dependency."""
    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        return s

    out: list[str] = []
    para: list[str] = []
    items: list[str] = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items)
                       + "</ul>")
            items.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            flush_list()
            continue
        if re.fullmatch(r"-{3,}", line.strip()):
            flush_para()
            flush_list()
            out.append("<hr>")
            continue
        m = re.match(r"(#{1,4})\s+(.*)", line)
        if m:
            flush_para()
            flush_list()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        if line.lstrip().startswith("- "):
            flush_para()
            items.append(line.lstrip()[2:].strip())
            continue
        if items and raw.startswith("  "):
            items[-1] += " " + line.strip()
            continue
        flush_list()
        para.append(line.strip())
    flush_para()
    flush_list()
    return "\n".join(out)


CATEGORY_BLURBS = {
    "long-context": "Precision retrieval across a large window. Needles sit "
        "among near-identical distractors, so a model must find the RIGHT one, "
        "respect recency when a fact is superseded, and aggregate across the "
        "whole window. Failure *depth* is the signal: which window size a model "
        "breaks at says more than a pass/fail.",
    "coding-python": "Write a correct implementation from scratch, without the "
        "library that would trivialise it. Parsing, edge cases, algorithmic "
        "correctness. Several of these are rumination traps — they look like "
        "they demand deep thought but reward a model that simply reads the spec.",
    "reasoning": "Deduction under interference: irrelevant numbers, precise "
        "instructions, and 'twisted classics' — famous puzzles with one premise "
        "changed. Those punish a memorised answer and reward actually reading.",
    "agentic": "Tier 2. The model gets tools and a private workspace and must "
        "explore, edit, and verify its own work. Scored on the WORKSPACE it "
        "leaves behind — not on what it claims it did — so a model that talks a "
        "good game but writes nothing scores zero.",
    "one-shot-apps": "One self-contained app.html in a single shot, graded by a "
        "headless browser that really clicks, drags, types, and reloads it. "
        "Partial credit for each behavior that genuinely works.",
}

LANE_BLURBS = [
    ("pytest", "coding-python · agentic",
     "A checker test-suite runs against the model's workspace. "
     "Score = fraction of tests that pass."),
    ("answer", "reasoning · long-context · math",
     "The final <code>ANSWER:</code> line is matched exactly, numerically "
     "(with tolerance), or by regex. Score is 1 or 0."),
    ("response", "instruction-following · hallucination · extraction · tool-use",
     "The model's whole reply is saved and a checker inspects it directly — "
     "format/constraint adherence, JSON field accuracy, grounded-answer vs "
     "correct abstention, or the right prompt-based tool call. "
     "Score = fraction of checks that pass."),
    ("webapp", "one-shot-apps",
     "The model's <code>app.html</code> is driven by headless Chromium "
     "(Playwright), which asserts real behavior. Score = fraction passing. "
     "A render task may cap this lane and hand the rest to a human — see "
     "<a href=\"#human\">Human-graded craft</a>."),
]

METRIC_GLOSSARY = [
    ("Score", "0–1. Pass fraction for pytest/webapp lanes; 1 or 0 for the "
     "answer lane. The leaderboard averages a model's <em>latest</em> score per "
     "task. One render task splits its score with a human reviewer — see "
     "<a href=\"#human\">Human-graded craft</a>."),
    ("Wall", "Total elapsed time for the task <strong>including every "
     "retry</strong>. The clock never lies — a model that needed three attempts "
     "pays for three attempts."),
    ("TTFT", "Time to first token (streaming only). How long the model thinks "
     "before it starts speaking."),
    ("tok/s", "Generation speed: output tokens ÷ generation time."),
    ("prefill tok/s", "Prompt-processing speed: input tokens ÷ time-to-first-"
     "token. This is what long-context tasks stress."),
    ("Tokens in/out", "Taken from the provider's own <code>usage</code> field — "
     "never estimated."),
    ("Cost", "Billed cost when the gateway reports it (OpenRouter), otherwise "
     "computed from the list pricing in the model's yaml. Which basis was used "
     "is recorded per result."),
    ("Retries", "Extra attempts consumed. Errors AND format failures (no ANSWER "
     "line, no code block) both burn an attempt."),
    ("Tries/pass", "Attempts spent per <em>perfect</em> (1.0) result — an "
     "efficiency measure. Lower is better; a model that one-shots everything "
     "sits at 1.0."),
    ("Attributed score", "The score with failures that were <strong>not the "
     "model's fault</strong> (harness bugs, infrastructure errors) removed. The "
     "gap between raw and attributed score is how much the harness cost that "
     "model."),
    ("Cold start", "Local models only: the measured <code>lms load</code> time "
     "before timing begins."),
]

STATUS_GLOSSARY = [
    ("ok", "good", "The model responded and the result was scored normally."),
    ("error", "bad", "Every attempt failed (timeout, connection, API error, or "
     "no usable output). Scored 0 — a real failure, and it counts."),
    ("max_turns", "warn", "A tier-2 model used up its agent turns before "
     "finishing. Its workspace is still graded as-is, so a partly-finished job "
     "can still earn partial credit."),
    ("⏸ usage limit", "warn", "A Claude subscription cap (5-hour / daily / "
     "weekly) was hit mid-run. The in-flight task is dropped <strong>unscored"
     "</strong> — deliberately NOT a zero — that model's remaining tasks are "
     "skipped, and the reset time is recorded. Re-run after the reset and the "
     "gap fills in."),
    ("skipped", "dim", "The task is tier 2 and the model has "
     "<code>supports_tools: false</code>. No result is recorded."),
]

CAVEATS = [
    ("Tier-2 isn't strictly apples-to-apples.",
     "Claude models run agentic tasks through <strong>Claude Code's own agent "
     "harness</strong> (its native tools, in the task workspace); every other "
     "model runs the harness's generic tool loop. Both are recorded — "
     "transcripts carry <code>agent_harness</code> — but a tier-2 gap between "
     "Claude and a local model is partly a gap between two agent scaffolds, not "
     "purely between two models."),
    ("A cloud model's serving host can drift between runs.",
     "OpenRouter routes to whichever provider it likes, and providers differ in "
     "precision (fp8 / fp4 / unknown). Each result records who actually served "
     "it and at what quantization — shown as <em>via &lt;host&gt; (quant)</em>. "
     "If a model's score moves between runs, check that column before blaming "
     "the model."),
    ("Cost is an estimate, not an invoice.",
     "Most cost figures are <strong>computed from a list price captured when the "
     "model was registered</strong> — a snapshot, not a live rate. Only results "
     "where the gateway reported an actual billed amount (marked <b>✓</b>) are "
     "authoritative. Published rates change, and a gateway routes the same model "
     "to different upstream hosts at different prices. See <a href=\"#pricing\">"
     "Pricing</a> below for exactly how many of these numbers are snapshots."),
    ("The answer lane is all-or-nothing.",
     "A right answer in the wrong format scores 0. That's deliberate — "
     "following the output contract is part of the task — but a 0 here doesn't "
     "always mean the model didn't know. Any 0 whose expected value is sitting "
     "inside the ANSWER line gets flagged <code>[FORMAT-MISS]</code> so it can "
     "be reviewed rather than quietly averaged in."),
    ("Old archived datasets are not comparable to the current one.",
     "Several agentic checkers used to hand out free credit for doing nothing "
     "(a no-op scored up to 0.80 on ag-007). Those floors were removed in v0.5.5 "
     "and v0.5.6, and live results were rescored — but archived datasets keep "
     "their original scores, by design. Compare within a dataset, not across "
     "them."),
    ("Timing-scored tasks are calibrated, not absolute.",
     "ag-006 grades an <em>algorithmic</em> speedup, and the naive solution is "
     "orders of magnitude slower than the optimised one. But an absolute "
     "wall-clock budget would measure how busy the machine was rather than how "
     "good the model was — we learned that the hard way when a correct 0.3s "
     "submission scored <strong>zero</strong> on a loaded box. The budget now "
     "times a fixed reference workload in the same subprocess and scales itself "
     "to the machine's current speed, so the verdict holds under load. The "
     "harness also refuses to rescore while a run is executing, because that "
     "contention corrupts the very budgets it is measuring."),
    ("Speed numbers only mean something on identical hardware.",
     "Every run stores its own hardware fingerprint. If two runs were measured "
     "on different rigs, their tok/s are not comparable — the fingerprints are "
     "shown below so you can check."),
]

CHART_GUIDE = [
    ("Efficiency frontier",
     "Average score against average output tokens per task. <strong>Up is "
     "better, left is cheaper.</strong> A model that answers correctly in 200 "
     "tokens beats one that ruminates for 2,000 to reach the same place — the "
     "top-left corner is where you want to live."),
    ("Rank across suite versions (bump chart)",
     "How each model's rank moved as the test suite evolved. Hover a node to "
     "highlight that model across every version; models tied at a rank share "
     "the node. Rank shifts here usually mean the <em>tests</em> got harder, "
     "not that a model got worse."),
    ("Value scatters (score vs cost / speed)",
     "The leaderboard ranks on score alone, which saturates at the top — the "
     "best few sit within a couple of percent. These scatters separate them on "
     "what actually differs: <strong>cost</strong> (API dollars to run the whole "
     "suite; a local model's dollar is just electricity, so that chart is "
     "API-only) and <strong>speed</strong> (tok/s, with a local/remote toggle). "
     "The dashed line is the <strong>Pareto frontier</strong>; a <em>dimmed</em> "
     "dot is <strong>dominated</strong> — some other model scores at least as "
     "high while costing less or running faster, so it is never the rational "
     "pick. Hover shows every model under the cursor."),
    ("Colours and dots",
     "Every chart on the overview shares <strong>one colour per model</strong>, "
     "so a model is the same colour everywhere. Charts are dots rather than "
     "lines because runs are discrete measurements, not a continuous signal — "
     "connecting them would imply a trend that isn't there."),
]

INFO_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Testing · Info</title><style>{{ css }}
.info h2 { margin-top:34px; padding-top:14px; border-top:1px solid var(--border); }
.info h3 { margin-top:22px; }
.info p, .info li { color:var(--ink); line-height:1.65; }
.info code { background:var(--surface2); padding:1px 5px; border-radius:4px;
  font-size:12.5px; }
.toc { display:flex; flex-wrap:wrap; gap:8px; margin:18px 0 6px; }
.toc a { font-size:12.5px; background:var(--surface2); border:1px solid var(--border);
  border-radius:999px; padding:4px 11px; text-decoration:none; color:var(--accent); }
.toc a:hover { border-color:var(--accent); }
.catcard { border:1px solid var(--border); border-radius:10px; padding:14px 16px;
  margin:12px 0; background:var(--surface); }
.catcard .h { display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; }
.catcard .h b { font-size:15px; }
.tasklist { margin-top:10px; font-size:12.5px; color:var(--ink-dim); }
.tasklist span { display:inline-block; margin:2px 10px 2px 0; }
.changelog h2 { border-top:none; margin-top:26px; font-size:17px; }
.changelog h3 { font-size:14px; }
.changelog hr { border:0; border-top:1px solid var(--border); margin:18px 0; }
.pill { font-size:11px; border:1px solid var(--border); border-radius:999px;
  padding:1px 8px; color:var(--ink-dim); }
</style></head><body>
<div class="topbar">
  <div><h1>LLM Testing</h1>
  <div class="sub">what the tests do · what the numbers mean · changelog</div></div>
  <div class="nav">{{ nav }}</div>
</div>
<div class="wrap info">

<div class="toc">
  <a href="#what">What this is</a><a href="#lanes">Scoring lanes</a>{% if human_graded %}<a href="#human">Human-graded craft</a>{% endif %}
  <a href="#tiers">Tiers</a><a href="#cats">Categories</a>
  <a href="#catalog">Task catalog</a><a href="#metrics">Metrics</a>
  <a href="#status">Run statuses</a>
  <a href="#fail">Failure taxonomy</a><a href="#fit">Task fit</a>
  <a href="#charts">Reading the charts</a>
  <a href="#method">Methodology</a><a href="#caveats">Caveats</a>
  <a href="#pricing">Pricing</a>
  <a href="#hw">Hardware</a><a href="#data">Raw data</a>
  <a href="#versions">Versioning</a><a href="#changelog">Changelog</a>
</div>

<h2 id="what">What this is</h2>
<p>A benchmark harness that runs the <strong>same {{ n_tasks }} tasks</strong>
against every model — local (LM Studio) and cloud (Claude subscription CLI,
OpenRouter) — and records timing, tokens, cost and retries for each one.
Currently <strong>suite v{{ suite_version }}</strong>, with
<strong>{{ n_models }} models</strong> across <strong>{{ n_runs }} runs</strong>
in the live dataset.</p>
<p>Every task is a <strong>brand-new conversation</strong>: exactly one user
message goes to the model (plus tool round-trips inside a tier-2 task), never
anything carried over from a previous task. Transcripts record the message count
and roles per request, so isolation is auditable rather than merely asserted.
Runs are sequential by default, because local models share one GPU and parallel
requests would corrupt the timing.</p>
<p><strong>Failing is fine.</strong> The hard tasks exist so models have headroom
to grow into. A model that solves 128k-token recall today tells you more than ten
models tied at 1.00 on easy tasks.</p>

<h2 id="lanes">Scoring lanes</h2>
<p>Three ways a task can be graded. The lane is a property of the task, not the
model.</p>
<table><thead><tr><th>Lane</th><th>Used by</th><th>How the score is produced</th></tr></thead>
<tbody>{% for name, cats, how in lanes %}
<tr><td><code>{{ name }}</code></td><td class="small">{{ cats }}</td>
<td class="small">{{ how|safe }}</td></tr>{% endfor %}
</tbody></table>

{% if human_graded %}
<h2 id="human">Human-graded craft</h2>
<p>Every score on this site is machine-produced and reproducible — with one
stated exception. {% for h in human_graded %}<code>{{ h.id }}</code>{% if not loop.last %}, {% endif %}{% endfor %}
{% if human_graded|length == 1 %}is a <em>render</em> task{% else %}are <em>render</em> tasks{% endif %}:
the point is how the result <em>looks</em>, and a checker cannot judge that. It
can verify <strong>mechanics</strong> — that the coin turns in 3D, carries a
specular that actually moves, is struck on both faces, has a reeded rim, and that
the site's states are right. It cannot see whether the lettering is mirrored, or
whether the thing looks like money.</p>
<p>So the machine's verdict is capped and the rest is awarded by a person on the
operator's review page:</p>
<table><thead><tr><th>Task</th><th class="num">Machine max</th>
<th class="num">Human craft</th><th>How the craft points are set</th></tr></thead>
<tbody>{% for h in human_graded %}
<tr><td><code>{{ h.id }}</code><div class="small">{{ h.title }}</div></td>
<td class="num"><strong>{{ h.cap }}</strong></td>
<td class="num"><strong>{{ h.craft }}</strong></td>
<td class="small">Two 0–10 sliders — <em>animation quality</em> and
<em>visual craft</em> — worth 0.00–0.10 each (zero is a real answer: mechanics can be certified with no craft awarded). A reviewer also confirms or
corrects each factor the checker decided; the score is computed from those
ticks, never typed.</td></tr>{% endfor %}
</tbody></table>
<p class="small muted" style="margin-top:8px">
Score = (factors confirmed ÷ total) × {{ human_graded[0].cap_v }} + animation/100
+ coin/100. Everything confirmed at 10/10 is exactly 1.0 and nothing else reaches
it — <strong>a submission nobody has reviewed tops out at {{ human_graded[0].cap }}</strong>,
by design. The machine's own number is never destroyed: it is kept alongside, and
clearing the review restores it. Which model produced which result stays hidden
from nothing here — but the factors, the sliders and the reviewer's note are all
recorded next to the result, so a craft score always shows its reasons.</p>
<p class="small muted">Why this task and no other: a checker that scores taste
would be a checker nobody can reproduce. Capping the machine at mechanics keeps
the other {{ n_tasks - human_graded|length }} tasks fully automatic and honest
about it.</p>
{% endif %}

<h2 id="tiers">Tiers</h2>
<p><strong>Tier 1 — single-shot.</strong> Prompt in, response out. Every model
can attempt these.</p>
<p><strong>Tier 2 — agentic.</strong> The model gets
<code>list_files</code> / <code>read_file</code> / <code>write_file</code> /
<code>run_python</code> in a private workspace and iterates until it's done.
Models with <code>supports_tools: false</code> skip these automatically. Claude
models run through Claude Code's own agent harness instead of the generic tool
loop — transcripts record which harness was used, so the comparison stays
honest.</p>

<h2 id="cats">Categories</h2>
{% for c in categories %}
<div class="catcard">
  <div class="h"><b>{{ c.name }}</b>
    <span class="pill">{{ c.n }} task{{ '' if c.n == 1 else 's' }}</span>
    <span class="pill">tier {{ c.tiers }}</span>
    <span class="pill">{{ c.lanes }} lane</span></div>
  <p class="small" style="margin:8px 0 0">{{ c.blurb }}</p>
  <div class="tasklist">{% for t in c.tasks %}<span>{{ t }}</span>{% endfor %}</div>
</div>
{% endfor %}

<h2 id="catalog">Task catalog</h2>
<p class="small">Every task in the live suite. Click a task to see how each model
did on it, side by side, with their verbatim output.</p>
<table><thead><tr><th>Task</th><th>Title</th><th>Category</th>
<th>Tier</th><th>Lane</th></tr></thead><tbody>
{% for t in tasks %}
<tr><td><a href="tasks/{{ t.id }}.html"><code>{{ t.id }}</code></a></td>
<td>{{ t.title }}</td><td class="small">{{ t.category }}</td>
<td class="small">{{ t.tier }}</td><td class="small"><code>{{ t.lane }}</code></td></tr>
{% endfor %}
</tbody></table>

<h2 id="metrics">What the numbers mean</h2>
<table><thead><tr><th>Metric</th><th>Meaning</th></tr></thead><tbody>
{% for name, meaning in metrics %}
<tr><td style="white-space:nowrap"><strong>{{ name }}</strong></td>
<td class="small">{{ meaning|safe }}</td></tr>
{% endfor %}
</tbody></table>

<h2 id="status">Run statuses</h2>
<p>What a result's <em>status</em> means, before any scoring is applied.</p>
<table><thead><tr><th>Status</th><th>Meaning</th></tr></thead><tbody>
{% for name, kind, meaning in statuses %}
<tr><td style="white-space:nowrap"><code>{{ name }}</code></td>
<td class="small">{{ meaning|safe }}</td></tr>
{% endfor %}
</tbody></table>

<h2 id="fail">Failure taxonomy</h2>
<p>Every non-passing result is classified, and each class is
<strong>attributed</strong> — to the model, to the harness, or to
infrastructure. This is what separates "the model got it wrong" from "we broke
it", and it's what the <em>attributed score</em> corrects for.</p>
<table><thead><tr><th>Class</th><th>Blame</th><th>Meaning</th></tr></thead><tbody>
{% for name, who, desc in failures %}
<tr><td><code>{{ name }}</code></td>
<td class="small"><span class="pill">{{ who }}</span></td>
<td class="small">{{ desc }}</td></tr>
{% endfor %}
</tbody></table>

<h2 id="fit">Task fit</h2>
<p>On the overview, every model is classified per category so you can pick the
right model for a job rather than just crowning one winner:</p>
<ul>
<li><strong>Top quality</strong> — the highest score in that category (ties share the crown).</li>
<li><strong>Value pick</strong> — the fastest generator that still clears the capable threshold.</li>
<li><strong>Also capable</strong> — clears the threshold, but isn't the best or the fastest.</li>
<li><strong>Below par</strong> — doesn't clear the threshold for this category.</li>
</ul>
<p class="small">The thresholds live in <code>directives.yaml</code> and are
<em>presentation</em>, not scoring: edit them and the classification updates on
the next report regeneration, with no suite version bump.</p>

<h2 id="charts">Reading the charts</h2>
{% for title, body in charts %}
<h3>{{ title }}</h3><p class="small">{{ body|safe }}</p>
{% endfor %}

<h2 id="method">Methodology guarantees</h2>
<ul>
<li><strong>Content-hashed tasks.</strong> Every result records a hash of the task
definition. Edit a task and the longitudinal report flags the break instead of
silently mixing versions.</li>
<li><strong>Every run counts — repeats aggregate.</strong> Test a model on a task
more than once in a version and the score becomes the <em>mean</em> of those
runs, not the newest: a second opinion fleshes the number out instead of
overwriting it, and the σ beside it is the spread. One model·task measured once
is simply the mean of one. Runs that never produced a score (crash, spiral,
DNF) stay out of the mean. A <em>rescore</em> still supersedes — it re-grades
the same run in place rather than adding one — and a genuinely botched run is
deleted on /manage rather than averaged in.</li>
<li><strong>Equal budget.</strong> Every non-Claude model gets the same
<code>max_tokens</code>. A model that died at a smaller budget is re-run before
its zeros are allowed to count.</li>
<li><strong>Local models run fully on the GPU (fixed 2026-07-18).</strong> Local
models are loaded with <code>--gpu max</code> and a context window sized to each
group of tasks. Before this, LM Studio's default "auto" offload left layers on
the CPU with VRAM free (gemma-4-31b: 8 tok/s at 17% GPU), and one 128k-context
task forced the whole run into a window too big to fit — so every task in the
run crawled. Now the short-context tasks load in a window that fits and run on
the GPU (~57 tok/s, 82%), and only genuine long-context tasks that exceed the
card pay the cost. <strong>This changes speed, not scores</strong> — same prompt,
budget, and weights. So tok/s, wall-clock, score/min, and energy for large local
models step up on this date and are not comparable to earlier runs; score-based
views (leaderboard, version-over-version) stay valid. Each run records its load
plan in <code>model_meta.json</code>.</li>
<li><strong>Reference-verified tasks.</strong> A new or changed task ships only
once a known-good implementation scores 1.0 <em>and</em> an empty or trap
submission scores 0. This is what catches checkers that hand out free credit for
doing nothing.</li>
<li><strong>Honest wall time.</strong> Retries are counted in it. Tokens come
from the provider's usage field, never estimated.</li>
<li><strong>Append-only ground truth.</strong> <code>runs/</code> holds full
transcripts, metrics, scores and the model's actual workspace. Reports are a pure
function of it — delete <code>reports/</code> and regenerate at any time.</li>
</ul>

<h2 id="contamination">Contamination &amp; memorization</h2>
<p>The hard question for any benchmark is whether a model scores well because it
<em>reasons</em> or because it has <em>seen the answer</em> in training. We can't
prove a private model's training set, so instead of claiming immunity we design
the tasks to make memorization not pay, and we tell you exactly how:</p>
<ul>
<li><strong>Original constructions, not public sets.</strong> The tasks are
written for this suite. They are not lifted from MMLU, HumanEval, GSM8K, or any
public leaderboard, so a model that memorized those gains nothing here.</li>
<li><strong>Twisted classics.</strong> Several reasoning tasks take a famous
puzzle and change the constraint that matters (the reversed river-crossing, the
Monty <em>Fall</em> variant). A model regurgitating the well-known answer scores
<em>zero</em> — the memorized response is now the wrong one. That is a
contamination detector, not just a question.</li>
<li><strong>Behaviour over recall.</strong> The one-shot-app and agentic tasks
are graded on what the model <em>builds</em> — a Playwright suite drives the
generated app, a pytest checker runs the model's code. You cannot memorize your
way through "make this maze solvable"; the artifact either works or it doesn't.</li>
<li><strong>Fresh long-context payloads.</strong> Long-context tasks assemble
their haystack at generation time, so the specific facts to retrieve aren't a
fixed string sitting in any crawl.</li>
<li><strong>Content-hashed and dated.</strong> Every result records the task's
content hash and the run date, so if a task ever leaked and were quietly
revised, the break is visible rather than silent — and you can see whether a
model was tested before or after a given model's training cutoff.</li>
</ul>
<p class="small">What we do <em>not</em> claim: that any closed model definitely
never saw a task. We claim the tasks are built so that seeing them helps little,
and that the twisted-classic scores are direct evidence a model is reasoning
rather than reciting.</p>

<h2 id="samplesize">Sample size &amp; how much to trust a number</h2>
<p>Be a skeptic — here is exactly how much data is behind each figure, stated
plainly rather than buried.</p>
<ul>
<li>This dataset holds <strong>{{ ss.n_runs }} runs</strong> across
<strong>{{ ss.n_models }} models</strong> and <strong>{{ ss.n_tasks }}
tasks</strong>, for <strong>{{ ss.n_cells }} scored model·task cells</strong>
totalling <strong>{{ ss.n_trials }} individual graded trials</strong>.</li>
<li><strong>Trials per cell.</strong> {{ ss.repeat_pct }}% of cells are backed by
more than one run; the rest are a single trial. A cell run more than once shows
its spread (σ) and its mean is over every scored run — see the aggregation rule
above.</li>
<li><strong>The headline band.</strong> Each model's score carries a 95%
confidence band (±1.96·SE) computed <em>across the task set</em> — treating the
{{ ss.n_tasks }} tasks as a sample. Two models whose bands overlap are not
distinguishable on this suite; the overview marks them tied (≈). This is why the
top cohort reads as a near-tie rather than a clean ranking.</li>
<li><strong>Small by design, honest about it.</strong> {{ ss.n_tasks }} tasks is
a deliberately small, hand-verified set, not a scraped thousand. Only a handful
currently separate the frontier models (see <a href="discriminate.html">task
discrimination</a>) — the number the suite is least sure of is <em>who is #1
among the top few</em>, and it says so rather than manufacturing a decisive
gap.</li>
</ul>

<h2 id="caveats">Caveats — read this before trusting a number</h2>
<p>Every benchmark has edges where the number means less than it looks like it
does. These are ours.</p>
{% for title, body in caveats %}
<div class="catcard"><div class="h"><b>{{ title }}</b></div>
<p class="small" style="margin:8px 0 0">{{ body|safe }}</p></div>
{% endfor %}

<h2 id="pricing">Pricing — read this before quoting a cost</h2>
<p>Every dollar figure on this site is an <strong>estimate of what a run would
have cost</strong>, not a bill. Four things are true at once, and all of them
matter:</p>
<ul>
<li><strong>The list price is a snapshot, not a live rate.</strong> A model's
<code>$/Mtok</code> is captured in its yaml <em>when the model is registered</em>
and does not update itself. Providers change their prices; this site does not
notice. <strong>{{ price_list }} of {{ price_total }} cost figures
({{ price_list_pct }}) are computed from that snapshot.</strong></li>
<li><strong>Only billed figures are authoritative.</strong> When the gateway
reports what it actually charged, we use that and mark it <b>✓</b>. That is
{{ price_billed }} of {{ price_total }} results ({{ price_billed_pct }}) — the
rest are arithmetic.</li>
<li><strong>The same model is served by different providers at different
prices.</strong> OpenRouter routes to whichever upstream it likes, and they differ
in price <em>and in quantization</em>. Across this dataset the catalog was served
by <strong>{{ hosts|length }} different hosts</strong>{% if hosts %}
({{ hosts[:6]|join(', ') }}{% if hosts|length > 6 %}, …{% endif %}){% endif %}.
A model's cost — and its score — can move between runs without the model changing
at all.</li>
<li><strong>Claude subscription runs report the API-equivalent price</strong>, not
what the subscription actually costs you. Treat those as "what this would have
cost on the API", not as spend. The estimate applies <strong>Anthropic cache
pricing</strong> — a re-read (cache-hit) input token is billed at 0.1&times; and a
cache write at 1.25&times; the base rate — so a multi-turn agentic run isn't
charged full price for re-sending its context each turn. Runs recorded before
this was added lack the cache breakdown and read high until the model is re-run.</li>
</ul>

<h3 id="freetier">"Free" models are on a promotion, not a price</h3>
<p>OpenRouter publishes promotional variants with a <code>:free</code> suffix on
the model id (<code>tencent/hy3:free</code>). Their <code>$0</code> is a
<em>true record</em> of what those runs were billed — but it is a promotion with
an end date, not a rate you can plan around. Treating it as a price is how a
benchmark starts recommending something that costs money tomorrow.</p>
<p>So the site separates two very different zeroes:</p>
<ul>
<li><strong>A local model's <code>$0</code> is durable</strong> — it is measured
GPU electricity (see below). It cannot expire.</li>
<li><strong>A <code>:free</code> gateway model's <code>$0</code> is temporary</strong>
— shown with a <b>⏳ free-tier</b> marker, and deliberately <em>excluded</em> from
the "cheapest that works" recommendation on <a href="#fit">Task fit</a>, where it
appears separately as "free now". Speed does not expire, so it can still win
"fastest that works".</li>
</ul>
<p>This is not hypothetical: a price refresh of this catalog found
<strong>four free tiers had already ended</strong> and one model's price had
nearly doubled since it was registered. Prices carry a
<code>pricing_asof</code> date for exactly this reason, and re-reading the live
catalog is a one-command operation — but until it is re-read, every list price
here is a snapshot of the day the model was registered.</p>

<h3>Local models are not free — they just bill you differently</h3>
<p>No money goes to a provider, so a local model's <code>$</code> column is ~0.
The wall socket still charges you. The harness samples the GPU throughout every
local run, so this is <strong>measured, not modelled</strong>: peak/average power,
and total watt-hours. The <strong>Power cost</strong> column turns that into money
at your rate — currently <code>{{ power_rate }}</code> per kWh, set in
<code>directives.yaml</code> (change it and the next report regeneration picks it
up; it's presentation, so no version bump).</p>
<p class="small">Two limits you must keep in mind, or this number will flatter
local models:</p>
<ul class="small">
<li><strong>It is GPU-only.</strong> It excludes the CPU, RAM, board, PSU losses
and cooling — so it is a <em>lower bound</em> on what the machine actually pulls
from the wall, not a utility bill.</li>
<li><strong>It is marginal, and ignores the hardware.</strong> It says nothing
about the cost of the GPU itself. Amortised over any realistic life, the card
dwarfs the electricity it will ever burn running this suite. A local model is
cheap <em>per run</em>; it was not cheap to own.</li>
</ul>
<p>Because of that measurement, a local model's <strong>Cost / run</strong> is its
<em>electricity</em>, marked <b>⚡</b> — not <code>$0</code>. It used to read
"free", which is exactly the unexamined assumption this project exists to
puncture. <strong>Score / $</strong> follows: a local model is now ranked on value
instead of hiding behind "free".</p>
<p class="small"><strong>But the comparison is not symmetric, and you must hold
this in your head:</strong> a cloud model's price includes <em>the provider's</em>
hardware, power, staff and margin. A local model's ⚡ figure includes none of
yours — not the GPU, not the rest of the box. So "local scores thousands of points
per dollar and Opus scores less than one" is <em>true as marginal cost</em> and
<em>misleading as total cost of ownership</em>. The local number is a floor; the
cloud number is a price. Compare locals to locals with confidence, and locals to
cloud with your eyes open.</p>
<p class="small"><strong>Bottom line:</strong> cost here is sound for
<em>order-of-magnitude</em> comparison between models in the same dataset. It is
not sound for budgeting, for quoting a vendor's current price, or for comparing
costs across dates. If you need a real number, go to the provider.</p>

<h2 id="hw">Hardware</h2>
<p>Speed numbers (tok/s, prefill, wall) are only comparable across runs measured
on the <strong>same rig</strong>. Every run stores its own fingerprint, so this
is checkable rather than assumed.</p>
{% if envs %}
<table><thead><tr><th>GPU</th><th>OS</th><th>Python</th><th>Host</th>
<th>Runs</th></tr></thead><tbody>
{% for e in envs %}
<tr><td>{{ e.gpu }}</td><td class="small">{{ e.os }}</td>
<td class="small">{{ e.python }}</td><td class="small">{{ e.host }}</td>
<td class="small">{{ e.n }}</td></tr>
{% endfor %}
</tbody></table>
{% if envs|length > 1 %}
<p class="small"><strong>⚠ More than one hardware configuration appears in this
dataset.</strong> Scores remain comparable, but <em>speed</em> figures across
these runs are not.</p>
{% else %}
<p class="small">All {{ n_runs }} runs in this dataset were measured on one
configuration, so speed comparisons are sound.</p>
{% endif %}
{% else %}
<p class="small">No hardware fingerprint recorded yet.</p>
{% endif %}
<p class="small">Local models additionally record GPU telemetry per run — peak
VRAM, average power draw, and energy used — sampled while the model runs, plus
the measured <code>lms load</code> cold-start time.</p>

<h2 id="data">Where the raw data lives</h2>
<p><code>runs/</code> is append-only ground truth. Reports are a pure function of
it, so you can delete <code>reports/</code> and regenerate at any time — and you
can audit any number on this site down to the raw exchange that produced it.</p>
<table><thead><tr><th>Path</th><th>What's in it</th></tr></thead><tbody>
<tr><td><code>runs/&lt;run&gt;/run.json</code></td><td class="small">Run manifest:
suite version, models, task hashes, hardware fingerprint, and any pause
reason.</td></tr>
<tr><td><code>…/&lt;model&gt;/&lt;task&gt;/transcript.jsonl</code></td>
<td class="small">Every request and response, verbatim — including each retry and
every tool round-trip.</td></tr>
<tr><td><code>…/metrics.json</code></td><td class="small">Timing, tokens, cost,
retries, turns, and the per-attempt breakdown.</td></tr>
<tr><td><code>…/score.json</code></td><td class="small">The score, who produced
it, and the checker's own output.</td></tr>
<tr><td><code>…/workspace/</code></td><td class="small">The files the model
actually wrote. For agentic tasks <strong>this is what gets graded</strong>; for
one-shot apps it holds the <code>app.html</code> that was driven by the
browser.</td></tr>
</tbody></table>
<p class="small">You never need the filesystem to look: every completed task in
the run log carries a <strong>files →</strong> link, and the
<a href="/data/">/data browser</a> walks the whole tree in the page. Generated
<code>app.html</code> files open live, so you can play with what the model
built.</p>

<h2 id="versions">Versioning &amp; datasets</h2>
<p><code>SUITE_VERSION</code> versions the <em>test dataset</em>, not the code.
A <strong>minor</strong> bump means the tests or the methodology changed, and the
old data is archived first so live reports always show exactly one coherent
dataset. A <strong>patch</strong> bump is a scoring fix or a presentation change
within a dataset — patches never archive, because the archive key is
<code>major.minor</code>, so every <code>{{ suite_series }}.x</code> run
aggregates together. Use the dataset selector in the top-right of the overview to
view an archived set, rendered with its own task-definition snapshot.</p>

<h2 id="changelog">Changelog</h2>
<div class="changelog">{{ changelog|safe }}</div>

</div></body></html>"""


def build_info_page(runs: list[dict], tdefs: dict, dataset_label: str = "",
                    dataset_key: str = "live") -> str:
    from . import assess

    tasks = sorted(tdefs.values(), key=lambda t: (t.category, t.id))

    _td = {tid: info for tid, info in collect_task_data(runs).items()
           if tid in tdefs}
    _cells = _repeat = _trials = 0
    for _info in _td.values():
        for _e in _info["agg"].values():
            if (_e.get("n_scored") or 0) > 0:
                _cells += 1
                _trials += _e["n_scored"]
                if _e.get("n_runs", 1) > 1:
                    _repeat += 1
    ss = {
        "n_runs": len(runs),
        "n_models": len({res["model"] for r in runs for res in r["results"]}),
        "n_tasks": len(tdefs),
        "n_cells": _cells,
        "n_trials": _trials,
        "repeat_pct": round(100 * _repeat / _cells) if _cells else 0,
    }

    human_graded = []
    for t in tasks:
        cap = float((t.scoring or {}).get("automated_max", 1.0))
        if cap < 1.0:
            human_graded.append({
                "id": t.id, "title": t.title,
                "cap": f"{cap:.0%}", "craft": f"{1 - cap:.0%}",
                "cap_v": f"{cap:g}",
            })
    cats = []
    for cat in sorted({t.category for t in tasks}):
        ts = [t for t in tasks if t.category == cat]
        cats.append({
            "name": cat,
            "n": len(ts),
            "tiers": "/".join(str(x) for x in sorted({t.tier for t in ts})),
            "lanes": "/".join(sorted({t.scoring_type for t in ts})),
            "blurb": CATEGORY_BLURBS.get(cat, ""),
            "tasks": [t.id for t in ts],
        })

    version = config.suite_version()

    changelog_md = ""
    cl = config.ROOT / "CHANGELOG.md"
    if cl.is_file():
        cl_version = version if dataset_key == "live" else dataset_key
        changelog_md = _changelog_for_version(cl.read_text(encoding="utf-8"),
                                              cl_version)

    n_models = len({res["model"] for r in runs for res in r["results"]})

    env_counts: dict[tuple, int] = {}
    for r in runs:
        e = (r.get("manifest") or {}).get("env") or {}
        if not e:
            continue
        key = (e.get("gpu") or "—", e.get("os") or "—",
               e.get("python") or "—", e.get("host") or "—")
        env_counts[key] = env_counts.get(key, 0) + 1
    envs = [{"gpu": g, "os": o, "python": p, "host": h, "n": n}
            for (g, o, p, h), n in sorted(env_counts.items(),
                                          key=lambda kv: -kv[1])]

    n_billed = n_list = 0
    hosts: dict[str, int] = {}
    for r in runs:
        for res in r["results"]:
            if res.get("cost_source") == "billed":
                n_billed += 1
            elif res.get("cost_source") == "list":
                n_list += 1
            for h in (res.get("served_by") or []):
                hosts[h] = hosts.get(h, 0) + 1
    n_cost = n_billed + n_list or 1
    host_list = [h for h, _ in sorted(hosts.items(), key=lambda kv: -kv[1])]

    return _env.from_string(INFO_TEMPLATE).render(
        nav=_nav(""),
        css=BASE_CSS,
        suite_version=version,
        suite_series=".".join(version.split(".")[:2]),
        price_billed=n_billed, price_list=n_list, price_total=n_cost,
        price_billed_pct=f"{n_billed / n_cost:.0%}",
        price_list_pct=f"{n_list / n_cost:.0%}",
        hosts=host_list,
        power_rate=(f"{_power_cfg().get('currency', '$')}"
                    f"{_power_cfg().get('cost_per_kwh', 0)}"),
        human_graded=human_graded,
        dataset_label=dataset_label, dataset_key=dataset_key,
        n_tasks=len(tasks), n_models=n_models, n_runs=len(runs),
        ss=ss,
        categories=cats,
        lanes=LANE_BLURBS,
        metrics=METRIC_GLOSSARY,
        statuses=STATUS_GLOSSARY,
        caveats=CAVEATS,
        charts=CHART_GUIDE,
        envs=envs,
        failures=[(name, who, desc)
                  for name, (who, desc) in assess.CATEGORIES.items()],
        tasks=[{"id": t.id, "title": t.title, "category": t.category,
                "tier": t.tier, "lane": t.scoring_type} for t in tasks],
        changelog=_md_to_html(changelog_md) if changelog_md
                  else "<p class='small'>No CHANGELOG.md found.</p>",
    )


def _pearson(a: dict, b: dict) -> float | None:
    """Correlation of two model->score vectors over the models they share."""
    import statistics as st
    keys = set(a) & set(b)
    if len(keys) < 8:
        return None
    xa = [a[k] for k in keys]
    xb = [b[k] for k in keys]
    if st.pstdev(xa) == 0 or st.pstdev(xb) == 0:
        return 1.0 if xa == xb else None
    ma, mb = sum(xa) / len(xa), sum(xb) / len(xb)
    num = sum((x - ma) * (y - mb) for x, y in zip(xa, xb))
    den = (sum((x - ma) ** 2 for x in xa) * sum((y - mb) ** 2 for y in xb)) ** 0.5
    return num / den if den else None


def discrimination_stats(runs: list[dict], tdefs: dict) -> dict:
    """How well each task separates models. Per task: mean, spread (sd),
    ceiling/floor rates, and the top-vs-bottom-cohort gap. Plus redundant task
    clusters and the frontier-compression headline."""
    import statistics as st
    from itertools import combinations

    td = {tid: info for tid, info in collect_task_data(runs).items()
          if tid in tdefs}
    by_model: dict[str, list[float]] = {}
    for info in td.values():
        for m, e in info["agg"].items():
            if e["score"].get("status") == "scored":
                by_model.setdefault(m, []).append(e["score"]["score"])
    n_suite = len(tdefs) or 1
    complete = {m: v for m, v in by_model.items() if len(v) >= n_suite}
    means = {m: sum(v) / len(v) for m, v in (complete or by_model).items()}
    ranked = sorted(means, key=lambda m: -means[m])
    k = max(3, len(ranked) // 3)
    top, bot = set(ranked[:k]), set(ranked[-k:])
    top_spread = (means[ranked[0]] - means[ranked[k - 1]]) if len(ranked) >= k else 0.0

    rows, tvecs = [], {}
    for tid, info in td.items():
        sc = {m: e["score"]["score"] for m, e in info["agg"].items()
              if e["score"].get("status") == "scored"}
        if not sc:
            continue
        tvecs[tid] = sc
        vals = list(sc.values())
        n = len(vals)
        tvv = [sc[m] for m in top if m in sc]
        bvv = [sc[m] for m in bot if m in sc]
        top_mean = sum(tvv) / len(tvv) if tvv else None
        bot_mean = sum(bvv) / len(bvv) if bvv else None
        gap = (top_mean - bot_mean) if top_mean is not None and bot_mean is not None else None
        mean = sum(vals) / n
        sd = st.pstdev(vals) if n > 1 else 0.0
        pct1 = sum(1 for v in vals if v >= 0.999) / n
        pct0 = sum(1 for v in vals if v <= 0.001) / n
        t = tdefs[tid]
        if gap is not None and abs(gap) < 0.06 and mean > 0.9:
            flag = "dead"
        elif top_mean is not None and top_mean < 0.85:
            flag = "frontier"
        elif pct1 >= 0.7:
            flag = "ceiling"
        elif gap is not None and gap > 0.3:
            flag = "floor-gate"
        elif sd >= 0.28 and 0.2 <= mean <= 0.85:
            flag = "discriminator"
        else:
            flag = "mixed"
        rows.append({
            "tid": tid, "tier": t.tier, "lane": t.scoring_type,
            "cat": t.category, "n": n, "mean": mean, "sd": sd,
            "pct1": pct1, "pct0": pct0, "gap": gap,
            "top_mean": top_mean, "bot_mean": bot_mean, "flag": flag,
        })
    rows.sort(key=lambda r: (r["sd"], -(r["gap"] or 0)))

    clusters = []
    for a, b in combinations(sorted(tvecs), 2):
        c = _pearson(tvecs[a], tvecs[b])
        if c is not None and c > 0.985:
            clusters.append((round(c, 3), a, b))
    clusters.sort(reverse=True)

    hard = [r["tid"] for r in rows if r["flag"] in ("frontier", "discriminator")]
    easy = [r["tid"] for r in rows if r["flag"] in ("ceiling", "dead")]
    grank = {m: i for i, m in enumerate(ranked)}

    def _rank_on(subset: list[str]) -> list[dict]:
        """Rank models on one task subset; delta = shift vs the global rank."""
        bucket: dict[str, list[float]] = {}
        for tid in subset:
            for m, e in td[tid]["agg"].items():
                if e["score"].get("status") == "scored":
                    bucket.setdefault(m, []).append(e["score"]["score"])
        need = max(1, len(subset) // 2)
        out = sorted(
            ({"model": m, "mean": sum(v) / len(v), "n": len(v),
              "global": means.get(m)} for m, v in bucket.items() if len(v) >= need),
            key=lambda x: -x["mean"])
        for i, r in enumerate(out):
            gi = grank.get(r["model"])
            r["delta"] = (gi - i) if gi is not None else None
        return out

    hard_rank = _rank_on(hard)
    easy_rank = _rank_on(easy)

    return {
        "rows": rows,
        "clusters": clusters,
        "hard_subset": hard,
        "hard_rank": hard_rank,
        "easy_subset": easy,
        "easy_rank": easy_rank,
        "top_spread": top_spread,
        "cohort_k": k,
        "top_models": ranked[:k],
        "bot_models": ranked[-k:],
        "n_tasks": len(rows),
        "n_dead": sum(1 for r in rows if r["flag"] == "dead"),
        "n_ceiling": sum(1 for r in rows if r["flag"] == "ceiling"),
        "n_frontier": sum(1 for r in rows if r["flag"] == "frontier"),
        "n_discriminator": sum(1 for r in rows
                               if r["flag"] in ("discriminator", "frontier")),
        "mean_sd": (sum(r["sd"] for r in rows) / len(rows)) if rows else 0.0,
    }


_DISCRIM_FLAG = {
    "dead": ("#c33", "dead", "no separation — every model scores ~1.0"),
    "ceiling": ("#c90", "ceiling", "≥70% of models score a perfect 1.0"),
    "floor-gate": ("#69c", "floor-gate", "tops pass, but it catches weak models"),
    "discriminator": ("#4a4", "discriminator", "wide spread across the field"),
    "frontier": ("#2a8", "frontier-hard", "even the strongest models struggle — gold"),
    "mixed": ("#888", "mixed", "some separation, but no clean ceiling / floor / frontier pattern"),
}


DISCRIMINATE_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Testing · Discrimination</title><style>{{ css }}
.note { color:var(--ink-dim); font-size:13px; line-height:1.6; }
.legend { display:flex; flex-wrap:wrap; gap:10px; margin:14px 0; }
.legend span.k { font-size:11px; border-radius:9px; padding:1px 8px; }
/* the hard-subset swatches, folded into the who's-best table as one column */
.whosbest th.tasks, .whosbest td.tasks { padding-left:18px; vertical-align:middle; }
.whosbest .tasks .mx-cells { border:0; height:auto; padding:3px 0; }
.whosbest th.tasks { font-weight:600; white-space:nowrap; }
.whosbest tr.fleetrow td { border-top:1px solid var(--rule); color:var(--muted); }
</style></head><body>
<div class="topbar">
  <div><h1>LLM Testing</h1>
  <div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}task
  discrimination · suite v{{ suite_version }}</div></div>
  <div class="nav">{{ nav }}</div>
</div>
<div class="wrap">
<p class="note">A leaderboard tells you who won; this tells you <b>which tasks the
answer actually depends on</b>. A task everyone aces (or everyone fails)
separates nobody — it just adds noise. Sorted by spread (σ), weakest
discriminators first. Basis: every run per model·task, aggregated.</p>

<div class="tiles">
{% for t in tiles %}<div class="tile"><div class="v">{{ t.v }}{% if t.sub %}<span class="vsub" title="{{ t.sub_tip }}">{{ t.sub }}</span>{% endif %}</div><div class="k">{{ t.k }}</div></div>
{% endfor %}</div>

<div class="card" style="margin:14px 0;padding:12px 16px">
<b>Frontier compression.</b> The top {{ cohort_k }} models span just
<b>{{ top_spread }}</b> in mean score — so their ordering is largely inside the
noise, and most of the suite's separation is spent distinguishing weak models
from strong. The fix is more <b>frontier-hard</b> tasks (below), not more easy
ones.<br><span class="note">top cohort: {{ top_models }}<br>bottom cohort:
{{ bot_models }}</span></div>

{% macro standings(s, label) %}
<div class="card mx-scroll"><table class="sortable whosbest">
<tr><th data-type="num">#</th><th data-type="text">Model</th>
<th data-type="num">{{ label }}-subset score</th><th data-type="num">Global score</th>
<th data-type="num">Move</th>
{% if s.cats %}<th class="tasks">On each {{ label|lower }} task →
  <div class="mx-cells">{% for c in s.cats %}<div class="mx-grp" style="grid-template-columns:repeat({{ c.n }},15px);gap:3px"><span class="mx-clabel" title="{{ c.key }}" style="grid-column:1/-1">{{ c.code }} <span class="cn">{{ c.n }}</span></span></div>{% endfor %}</div></th>{% endif %}</tr>
{% for h in s.rank %}
<tr><td class="num">{{ h.rank }}</td><td class="nowrap">{{ h.model }}</td>
<td class="num" data-sort="{{ h.mean_v }}">{{ h.mean }}</td>
<td class="num">{{ h.glob }}</td><td class="num">{{ h.move }}</td>
{% if s.cats %}<td class="tasks"><div class="mx-cells">{% for g in h.groups %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div></td>{% endif %}</tr>
{% endfor %}
{% if s.cats %}<tr class="fleetrow"><td></td><td class="nowrap small">fleet avg / task →</td><td></td><td></td><td></td>
<td class="tasks"><div class="mx-cells">{% for g in s.foot %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div></td></tr>{% endif %}
</table></div>
<p class="note" style="margin-top:4px">{{ label }} subset ({{ s.n }}): {{ s.tasks }}</p>
{% endmacro %}

{% if hard.rank or easy.rank %}
<h2>Who's actually best — ranked on a task subset</h2>
<p class="note">The global leaderboard is inflated by tasks everyone aces.
<b>Hard</b> ranks models on only the tasks that separate the field (frontier +
wide-spread discriminators), where the real gaps live. <b>Easy</b> is the other
end — the tasks almost every model gets right; the ranking there is
<em>supposed</em> to be flat, and seeing it collapse is the point. <b>Move</b> is
the shift vs the global rank: <span style="color:#3a3">▲climbs</span> = stronger
on that subset than its overall score suggests,
<span style="color:#c55">▼drops</span> = was riding the other end.</p>
<div class="seg" id="sbseg">
  <button type="button" data-sb="hard" class="on">◆ Hard ({{ hard.n }})</button>
  <button type="button" data-sb="easy">Easy ({{ easy.n }})</button>
</div>
<div id="sb-hard">{{ standings(hard, 'Hard') }}</div>
<div id="sb-easy" style="display:none">{{ standings(easy, 'Easy') }}</div>
<script>
document.querySelectorAll('#sbseg button').forEach(b =>
  b.addEventListener('click', () => {
    document.querySelectorAll('#sbseg button').forEach(x => x.classList.toggle('on', x === b));
    document.getElementById('sb-hard').style.display = b.dataset.sb === 'hard' ? '' : 'none';
    document.getElementById('sb-easy').style.display = b.dataset.sb === 'easy' ? '' : 'none';
  }));
</script>
{% endif %}

<div class="legend">
{% for l in legend %}<span class="k" style="color:{{ l.color }};border:1px solid {{ l.color }}"
  title="{{ l.desc }}">{{ l.label }}</span>{% endfor %}</div>

<div class="card"><table class="sortable">
<tr><th data-type="text">task</th><th data-type="text">lane</th>
<th data-type="num">n</th><th data-type="num">mean</th>
<th data-type="num">σ spread</th><th data-type="num">%1.0</th>
<th data-type="num">%0</th><th data-type="num">top</th>
<th data-type="num">bottom</th><th data-type="num">gap</th><th data-type="text">verdict</th></tr>
{% for r in rows %}
<tr><td class="model">{{ r.tid }}</td><td class="small">{{ r.lane }}</td>
<td class="num">{{ r.n }}</td>
<td class="num" data-sort="{{ r.mean_v }}">{{ r.mean }}</td>
<td class="num" data-sort="{{ r.sd_v }}">{{ r.sd }}</td>
<td class="num" data-sort="{{ r.pct1_v }}">{{ r.pct1 }}</td>
<td class="num" data-sort="{{ r.pct0_v }}">{{ r.pct0 }}</td>
<td class="num" data-sort="{{ r.top_v }}">{{ r.top }}</td>
<td class="num" data-sort="{{ r.bot_v }}">{{ r.bot }}</td>
<td class="num" data-sort="{{ r.gap_v }}">{{ r.gap }}</td>
<td>{{ r.badge }}</td></tr>
{% endfor %}</table></div>
<p class="note"><b>top</b>/<b>bottom</b> = mean score of the strongest / weakest
cohort; <b>gap</b> is their difference (how sharply the task separates the
field). <b>%1.0</b> is the share of models scoring a perfect 1.0.</p>

{% if clusters %}
<h2>Redundant task clusters</h2>
<p class="note">These task pairs rank the models almost identically (Pearson
&gt; 0.985) — they measure the same thing. Candidates to collapse: keep one,
drop the rest, spend the budget on frontier-hard tasks.</p>
<div class="card"><table>
<tr><th class="num">r</th><th>task A</th><th>task B</th></tr>
{% for c in clusters %}<tr><td class="num">{{ c.c }}</td>
<td class="model">{{ c.a }}</td><td class="model">{{ c.b }}</td></tr>
{% endfor %}</table></div>
{% endif %}
</div>
{{ sort_js }}
</body></html>"""


def build_discriminate_page(runs: list[dict], tdefs: dict,
                            dataset_label: str = "",
                            dataset_key: str = "live") -> str:
    d = discrimination_stats(runs, tdefs)

    def cell(v, pct=False):
        if v is None:
            return "—"
        return f"{v * 100:.0f}%" if pct else f"{v:.2f}"

    trows = []
    for r in d["rows"]:
        color, label, _ = _DISCRIM_FLAG.get(r["flag"], ("var(--muted)", "", ""))
        badge = (f'<span style="color:{color};border:1px solid {color};'
                 f'border-radius:9px;padding:1px 7px;font-size:11px">{label}</span>'
                 if label else "")
        trows.append({
            "tid": r["tid"], "lane": f"T{r['tier']} {r['lane']}",
            "n": r["n"], "mean": cell(r["mean"]), "mean_v": f"{r['mean']:.4f}",
            "sd": cell(r["sd"]), "sd_v": f"{r['sd']:.4f}",
            "pct1": cell(r["pct1"], True), "pct1_v": f"{r['pct1']:.4f}",
            "pct0": cell(r["pct0"], True), "pct0_v": f"{r['pct0']:.4f}",
            "top": cell(r["top_mean"]), "top_v": f"{r['top_mean'] or 0:.4f}",
            "bot": cell(r["bot_mean"]), "bot_v": f"{r['bot_mean'] or 0:.4f}",
            "gap": cell(r["gap"]), "gap_v": f"{r['gap'] or 0:.4f}",
            "badge": badge,
        })

    tiles = [
        {"v": str(d["n_tasks"]), "k": "tasks scored"},
        {"v": f"{d['top_spread']:.2f}", "k": f"top-{d['cohort_k']} spread (smaller = frontier bunched)"},
        {"v": str(d["n_frontier"]), "k": "frontier-hard (best still struggle)"},
        {"v": str(d["n_ceiling"]), "k": "ceiling (≥70% score 1.0)"},
        {"v": str(d["n_dead"]), "k": "dead (no separation)"},
        {"v": f"{d['mean_sd']:.2f}", "k": "mean spread per task"},
    ]
    clusters = [{"c": f"{c:.3f}", "a": a, "b": b} for c, a, b in d["clusters"]]
    legend = [{"color": v[0], "label": v[1], "desc": v[2]}
              for v in _DISCRIM_FLAG.values()]

    def _move(delta):
        if not delta:
            return '<span class="note">—</span>'
        col = "#3a3" if delta > 0 else "#c55"
        return f'<span style="color:{col}">{"▲" if delta > 0 else "▼"}{abs(delta)}</span>'

    from . import assess
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    acfg = assess.load_cfg()
    suspect = assess.suspect_answers(task_data, tdefs, acfg)

    def _standings(subset_ids, rank_list):
        cat_tids: dict[str, list[str]] = {}
        for tid in subset_ids:
            cat_tids.setdefault(tdefs[tid].category, []).append(tid)
        for c in cat_tids:
            cat_tids[c].sort()
        cats_o = sorted(cat_tids)
        mx_cats = [{"key": c, "code": _cat_code(cat_tids[c]),
                    "n": len(cat_tids[c])} for c in cats_o]
        foot = []
        for c in cats_o:
            grp = []
            for tid in cat_tids[c]:
                vals = [e["score"]["score"] for e in task_data[tid]["agg"].values()
                        if e["score"].get("status") == "scored"
                        and e["score"].get("score") is not None]
                if vals:
                    v = sum(vals) / len(vals)
                    grp.append({"cls": "pass",
                                "a": f"{0.10 + 0.90 * max(0.0, min(1.0, v)):.3f}",
                                "tip": f"{tid} · fleet avg {v:.2f}",
                                "href": f"tasks/{tid}.html"})
                else:
                    grp.append({"cls": "na", "a": "0", "tip": f"{tid} · no data",
                                "href": f"tasks/{tid}.html"})
            foot.append(grp)
        rank = [{"rank": i + 1, "model": _mlink(h["model"]),
                 "mean": f"{h['mean']:.3f}", "mean_v": f"{h['mean']:.4f}",
                 "glob": (f"{h['global']:.3f}" if h["global"] is not None else "—"),
                 "move": _move(h["delta"]),
                 "groups": [[_mx_cell(task_data[tid]["agg"].get(h["model"]),
                                      tdefs[tid], acfg, suspect,
                                      f"tasks/{tid}.html#m-{_slug_name(h['model'])}")
                             for tid in cat_tids[c]] for c in cats_o]}
                for i, h in enumerate(rank_list)]
        return {"rank": rank, "cats": mx_cats, "foot": foot,
                "n": len(subset_ids), "tasks": ", ".join(subset_ids)}

    hard = _standings(d["hard_subset"], d["hard_rank"])
    easy = _standings(d["easy_subset"], d["easy_rank"])

    return _env.from_string(DISCRIMINATE_TEMPLATE).render(
        hard=hard, easy=easy,
        nav=_nav(""),
        sort_js=_SORT_JS, css=BASE_CSS, tiles=tiles, rows=trows,
        clusters=clusters, legend=legend,
        top_models=", ".join(d["top_models"]),
        bot_models=", ".join(d["bot_models"]),
        cohort_k=d["cohort_k"], top_spread=f"{d['top_spread']:.2f}",
        dataset_label=dataset_label, dataset_key=dataset_key,
        suite_version=config.suite_version())



def family_stats(runs: list[dict], tdefs: dict) -> dict:
    """Group models by family (yaml `family:` or inferred), with each member's
    suite mean, where it runs, and (for local models) its GGUF weight size."""
    from . import gguf
    from .registry import infer_family, load_models

    reg = {mo.name: mo for mo in load_models(include_disabled=True)}
    _, hidden = _model_prefs()
    td = {tid: info for tid, info in collect_task_data(runs).items()
          if tid in tdefs}
    n_suite = len(tdefs) or 1
    ent: dict[str, list[dict]] = {}
    for info in td.values():
        for m, e in info["agg"].items():
            if m not in hidden and e["score"].get("status") == "scored":
                ent.setdefault(m, []).append(e)

    _fp: dict[str, dict | None] = {}
    fams: dict[str, list[dict]] = {}
    for m, es in ent.items():
        mo = reg.get(m)
        fam = mo.family_name if mo else infer_family(m)
        if not fam:
            continue
        local = bool(mo.local) if mo else bool(
            (es[0].get("model_meta") or {}).get("local"))
        fp = None
        if mo and mo.local:
            if mo.model not in _fp:
                try:
                    _fp[mo.model] = gguf.footprint(mo.model)
                except Exception:
                    _fp[mo.model] = None
            fp = _fp[mo.model]
        tps_vals = [e.get("gen_tokens_per_sec") for e in es
                    if e.get("gen_tokens_per_sec")]
        weights = (fp or {}).get("weights_gb")
        vram_ref = None
        if fp:
            vram_ref = (fp["weights_gb"] + fp["kv_fixed_gb"]
                        + fp["kv_per_tok_gb"] * VRAM_REF_CTX)
        fams.setdefault(fam, []).append({
            "model": m, "score": sum(e["score"]["score"] for e in es) / len(es),
            "n": len(es), "coverage": len(es) / n_suite, "local": local,
            "weights_gb": weights, "vram_ref_gb": vram_ref,
            "native_ctx": (fp or {}).get("native_ctx"),
            "quant": (fp or {}).get("quant"),
            "tps": (sum(tps_vals) / len(tps_vals)) if tps_vals else None,
        })
    for f in fams:
        fams[f].sort(key=lambda x: -x["score"])
    return fams


def _size_score_svg(points: list[dict], colors: dict, width=1000, height=360) -> str:
    """Score (y) vs VRAM-GB (x) for local models, with the Pareto frontier — the
    best score achievable at each VRAM budget. One dot per model."""
    pts = [p for p in points if p.get("x") and p.get("y") is not None]
    if not pts:
        return ""
    pad_l, pad_r, pad_t, pad_b = 52, 16, 14, 44
    xmax = max(p["x"] for p in pts) * 1.08
    ymin = min(0.5, min(p["y"] for p in pts) - 0.05)
    ymin = max(0.0, ymin)

    def X(x):
        return pad_l + (x / xmax) * (width - pad_l - pad_r)

    def Y(y):
        return pad_t + (1 - (y - ymin) / (1 - ymin)) * (height - pad_t - pad_b)

    parts = [f'<svg viewBox="0 0 {width} {height}" style="width:100%;height:auto" '
             f'class="szchart" role="img" aria-label="score vs VRAM">']
    for gy in [ymin + (1 - ymin) * i / 4 for i in range(5)]:
        parts.append(f'<line x1="{pad_l}" y1="{Y(gy):.0f}" x2="{width - pad_r}" '
                     f'y2="{Y(gy):.0f}" stroke="var(--border)" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{Y(gy) + 4:.0f}" text-anchor="end" '
                     f'style="font:11px system-ui;fill:var(--muted)">{gy:.2f}</text>')
    for gx in range(0, int(xmax) + 1, 8):
        parts.append(f'<text x="{X(gx):.0f}" y="{height - pad_b + 16:.0f}" '
                     f'text-anchor="middle" style="font:11px system-ui;'
                     f'fill:var(--muted)">{gx}</text>')
    parts.append(f'<text x="{width / 2:.0f}" y="{height - 6:.0f}" text-anchor="middle" '
                 f'style="font:12px system-ui;fill:var(--ink-dim)">'
                 f'VRAM to run at {VRAM_REF_CTX // 1024}k context — weights + KV cache (GB)</text>')
    front, best = [], -1
    for p in sorted(pts, key=lambda p: p["x"]):
        if p["y"] > best + 1e-9:
            best = p["y"]
            front.append(p)
    if len(front) > 1:
        d = " ".join(f'{"M" if i == 0 else "L"}{X(p["x"]):.0f},{Y(p["y"]):.0f}'
                     for i, p in enumerate(front))
        parts.append(f'<path d="{d}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="2" stroke-dasharray="5 4" opacity="0.7"/>')
    for p in pts:
        c = colors.get(p["label"], "var(--accent)")
        cx, cy = X(p["x"]), Y(p["y"])
        tip = p.get("tip") or f'{p["label"]} · {p["x"]:.1f} GB · {p["y"]:.2f}'
        parts.append(
            f'<circle class="szdot" cx="{cx:.0f}" cy="{cy:.0f}" r="5.5" fill="{c}" '
            f'data-tip="{html.escape(tip, quote=True)}" '
            f'style="cursor:pointer"/>')
    parts.append("</svg>")
    return "".join(parts)


FAMILY_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Testing · Families</title><style>{{ css }}
.famcard { border:1px solid var(--border); border-radius:10px; padding:12px 16px;
  margin:12px 0; background:var(--surface); }
.famcard .h { display:flex; align-items:baseline; gap:10px; flex-wrap:wrap;
  margin-bottom:6px; }
.famcard .h b { font-size:15px; }
.note { color:var(--ink-dim); font-size:13px; line-height:1.6; }
.pill2 { font-size:11px; border:1px solid var(--accent); color:var(--accent);
  border-radius:999px; padding:1px 8px; }
</style></head><body>
<div class="topbar">
  <div><h1>LLM Testing</h1>
  <div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}model
  families · suite v{{ suite_version }}</div></div>
  <div class="nav">{{ nav }}</div>
</div>
<div class="wrap">
<p class="note">Models grouped by lineage — so you can read a family's
<b>size↔capability ladder</b> and see how a small local model stacks up against
its larger hosted sibling. A <span class="pill2">local + hosted</span> tag marks
a family you can compare across that line. Family is set on the
<b>Organize</b> page (a yaml <code>family:</code> key), else inferred from the
name — a model placed in <b>No-family</b> doesn't appear here.</p>

{% if verscmp %}
<h2>Version-over-version</h2>
<div class="card">
  <div class="vc-pick">
    <label>family<select id="vc-fam"></select></label>
    <label>from<select id="vc-a"></select></label>
    <label>to<select id="vc-b"></select></label>
    <span class="vc-note">members present in both versions, like-for-like tasks only</span>
  </div>
  <div id="vc-out"></div>
</div>
<script type="application/json" id="vc-data">{{ verscmp }}</script>
{{ verscmp_js }}
{% endif %}

{% if size_chart %}
<h2>Capability vs VRAM — local models</h2>
<div class="chartkey"><span class="k-dot"></span> a local model
  <span class="k-line"></span> <b>Pareto frontier</b> — best score per VRAM</div>
<div class="card chartcard">{{ size_chart }}</div>
<div class="note" style="margin-top:6px">Each dot is a local model: suite score
vs the <b>VRAM to actually run it</b> — weights (from the quant) <b>plus KV
cache</b> at 32k context. Hover anywhere near a dot to see <b>every</b> model
under the cursor (overlapping dots all list). The dashed line is the <b>Pareto
frontier</b> — the best score reachable at each VRAM budget; a dot below it is
beaten by something that needs less VRAM.</div>
{% endif %}

<h2>Best of each family</h2>
<div class="card"><table class="sortable">
<tr><th data-type="text">Family</th><th data-type="num">Members</th>
<th data-type="num">Best score</th><th data-type="text">Leader</th></tr>
{% for c in champs %}
<tr><td class="model">{{ c.name }}</td><td class="num">{{ c.n }}</td>
<td class="num" data-sort="{{ c.best }}">{{ c.best }}</td>
<td class="nowrap">{{ c.leader }}</td></tr>
{% endfor %}</table></div>

<h2>Within each family</h2>
{% for f in fam_cards %}
<div class="famcard">
<div class="h"><b>{{ f.name }}</b>
  <span class="note">{{ f.n }} models · {{ f.span }}</span>
  {% if f.both %}<span class="pill2">local + hosted</span>{% endif %}</div>
<table class="sortable"><tr><th data-type="text">Model</th>
<th data-type="text">Where</th><th data-type="num">Score</th><th></th>
<th data-type="num" title="VRAM to run at 32k = weights + KV cache">VRAM @32k</th>
<th data-type="num">tok/s</th></tr>
{% for r in f.rows %}
<tr><td class="nowrap">{{ r.model }}</td><td class="small">{{ r.where }}</td>
<td class="num" data-sort="{{ r.score_v }}">{{ r.score }}{{ r.cov }}</td>
<td>{{ r.bar }}</td><td class="num" data-sort="{{ r.size_v }}">{{ r.size }}</td>
<td class="num" data-sort="{{ r.tps_v }}">{{ r.tps }}</td></tr>
{% endfor %}</table></div>
{% endfor %}

{% if singles %}
<div class="note" style="margin-top:14px"><b>Single-model families</b> (no
within-family comparison yet): {{ singles }}. Set a shared <code>family:</code>
in their yamls to cluster them.</div>
{% endif %}
</div>
{{ scatter_js }}
{{ sort_js }}
</body></html>"""


def build_family_page(runs: list[dict], tdefs: dict, dataset_label: str = "",
                      dataset_key: str = "live",
                      versions: list[tuple] | None = None) -> str:
    from .registry import load_families
    fams = family_stats(runs, tdefs)
    order = [mm["model"] for f in fams.values() for mm in f]
    fam_of = {mm["model"]: fname for fname, ms in fams.items() for mm in ms}
    _, hidden = _model_prefs()
    colors = _model_colors(order, _model_prefs()[0], fam_of, load_families())

    refk = VRAM_REF_CTX // 1024

    def fmt(mm):
        if mm.get("vram_ref_gb"):
            size = (f'<span title="weights {mm["weights_gb"]:.1f} GB + KV cache at '
                    f'{refk}k context · {mm.get("quant") or "?"}">'
                    f'{mm["vram_ref_gb"]:.0f} GB</span>')
            size_v = f"{mm['vram_ref_gb']:.2f}"
        else:
            size = "—" if mm["local"] else "hosted"
            size_v = "0"
        return {
            "model": _mlink(mm["model"]),
            "where": "local ⚡" if mm["local"] else "hosted",
            "kind": "local" if mm["local"] else "hosted",
            "score": f"{mm['score']:.3f}", "score_v": f"{mm['score']:.4f}",
            "bar": bar(mm["score"], 1.0, width=90),
            "size": size, "size_v": size_v,
            "tps": (f"{mm['tps']:.0f}" if mm["tps"] else "—"),
            "tps_v": f"{mm['tps'] or 0:.1f}",
            "cov": ("" if mm["coverage"] >= 0.999 else " partial"),
        }

    multi = {f: v for f, v in fams.items() if len(v) > 1}
    singles = sorted(f for f, v in fams.items() if len(v) == 1)
    fam_cards = []
    for f in sorted(multi, key=lambda f: -max(x["score"] for x in multi[f])):
        members = multi[f]
        has_both = len({x["local"] for x in members}) > 1
        fam_cards.append({
            "name": f, "n": len(members),
            "span": f"{min(x['score'] for x in members):.3f}–"
                    f"{max(x['score'] for x in members):.3f}",
            "both": has_both, "rows": [fmt(x) for x in members],
        })

    champs = sorted(
        ({"name": f, "best": max(v, key=lambda x: x["score"])["score"],
          "leader": _mlink(max(v, key=lambda x: x["score"])["model"]),
          "n": len(v)} for f, v in fams.items()),
        key=lambda c: -c["best"])
    for c in champs:
        c["best"] = f"{c['best']:.3f}"

    pts = []
    for v in fams.values():
        for mm in v:
            if mm["local"] and mm.get("vram_ref_gb"):
                tip = (f'{mm["model"]} — score {mm["score"]:.3f} · '
                       f'{mm["vram_ref_gb"]:.0f} GB to run at {refk}k '
                       f'(weights {mm["weights_gb"]:.1f} + KV cache)'
                       + (f' · {mm["quant"]}' if mm.get("quant") else ''))
                pts.append({"x": mm["vram_ref_gb"], "y": mm["score"],
                            "label": mm["model"], "tip": tip})
    size_chart = _size_score_svg(pts, colors)

    verscmp = ""
    if versions:
        fam_of = _family_of_map(versions)
        members_by_fam: dict[str, set] = {}
        for name, fam in fam_of.items():
            if fam:
                members_by_fam.setdefault(fam, set()).add(name)
        blob = {}
        for fam, members in members_by_fam.items():
            if len(members) < 2:
                continue
            p = family_version_payload(fam, members, versions)
            if len(p["versions"]) >= 2 and p["pairs"]:
                blob[fam] = p
        if blob:
            import json as _json
            verscmp = _json.dumps({k: blob[k] for k in sorted(blob)}
                                  ).replace("</", "<\\/")
    return _env.from_string(FAMILY_TEMPLATE).render(
        nav=_nav(""),
        sort_js=_SORT_JS, scatter_js=_SCATTER_HOVER_JS,
        verscmp=verscmp, verscmp_js=_VERSCMP_JS,
        css=BASE_CSS, fam_cards=fam_cards, champs=champs,
        size_chart=size_chart, singles=", ".join(singles),
        dataset_label=dataset_label, dataset_key=dataset_key,
        suite_version=config.suite_version())


COMPARE_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compare · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">
  <div><h1>Head to head</h1>
  <div class="sub">two models, every task, side by side · {{ dataset_label or "live dataset" }}</div></div>
  <div class="nav">{{ nav }}</div>
</div>

<div class="cmp-pick">
  <select id="selA" class="cmp-sel"></select>
  <button id="swap" class="cmp-swap" title="swap sides">&#8646;</button>
  <select id="selB" class="cmp-sel"></select>
</div>

<div id="cmp-head" class="cmp-head"></div>
<h2>Per-task <span class="small muted" style="text-transform:none;letter-spacing:0;font-weight:400">· swatch ink ramps with the score · Δ colours the winner · grouped by category</span></h2>
<div id="cmp-grid"></div>

<script>const D = {{ data_json|safe }};</script>
<script>
const $ = s => document.querySelector(s);
function q(v){ // score -> swatch opacity
  return (0.10 + 0.90*Math.max(0,Math.min(1,v))).toFixed(3);
}
function sc(v){ // score -> {cls, txt, sw}
  if (v === null || v === undefined)
    return {cls:'muted', txt:'\\u2014', sw:'<span class="hsw pend"></span>'};
  const st = v >= 0.8 ? 'good' : (v >= 0.4 ? 'warn' : 'crit');
  return {cls:st, txt:v.toFixed(3),
          sw:'<span class="hsw" style="--a:'+q(v)+'"></span>'};
}
function num(x){ return (x === null || x === undefined) ? null : x; }
function fmtPct(v){ return v === null ? '\\u2014' : Math.round(v*100)+'%'; }

// metric rows: [label, key, higherBetter, format(model)->string]
const METRICS = [
  ['Raw score', 'score', true, m => m.score===null?'\\u2014':m.score.toFixed(3)+(m.ci!==null?' \\u00b1'+m.ci.toFixed(3).replace(/^0/,''):'')],
  ['Tasks \\u2265 0.80', 'passrate', true, m => m.graded?((m.pass/m.graded))?(m.pass+'/'+m.graded):'\\u2014':'\\u2014'],
  ['Cost / pass', 'cost', false, m => m.costStr],
  ['Gen tok/s', 'tps', true, m => m.tps===null?'\\u2014':m.tps.toFixed(1)],
  ['Total time', 'wall', false, m => m.timeStr],
  ['First-try clean', 'ft', true, m => fmtPct(m.ft)],
];
function metricVal(m, key){
  if (key==='passrate') return m.graded ? m.pass/m.graded : null;
  if (key==='cost') return num(m.costVal);
  if (key==='wall') return num(m.wall);
  if (key==='tps') return num(m.tps);
  if (key==='ft') return num(m.ft);
  return num(m.score);
}
function renderHead(a, b){
  const A = D.data[a], B = D.data[b];
  let h = '<table class="cmp-tbl"><thead><tr><th></th>'
        + '<th class="cmp-c"><a href="models/'+A.slug+'.html">'+a+'</a>'
        + '<div class="small muted">#'+A.rank+' \\u00b7 '+A.where+'</div></th>'
        + '<th class="cmp-d">\\u0394</th>'
        + '<th class="cmp-c"><a href="models/'+B.slug+'.html">'+b+'</a>'
        + '<div class="small muted">#'+B.rank+' \\u00b7 '+B.where+'</div></th></tr></thead><tbody>';
  for (const [label, key, hi, fmt] of METRICS){
    const va = metricVal(A, key), vb = metricVal(B, key);
    let wa='', wb='', delta='';
    if (va!==null && vb!==null && va!==vb){
      const aWins = hi ? va>vb : va<vb;
      wa = aWins ? 'win' : ''; wb = aWins ? '' : 'win';
    }
    if (va!==null && vb!==null){
      const d = va - vb;
      if (Math.abs(d) > 1e-9){
        const sign = d>0?'+':'';
        let dv = (key==='cost') ? sign+d.toFixed(4)
               : (key==='wall') ? '' : sign+(Math.abs(d)<1?d.toFixed(3):d.toFixed(1));
        delta = dv;
      }
    }
    h += '<tr><td class="cmp-k">'+label+'</td>'
       + '<td class="cmp-c '+wa+'">'+fmt(A)+'</td>'
       + '<td class="cmp-d">'+delta+'</td>'
       + '<td class="cmp-c '+wb+'">'+fmt(B)+'</td></tr>';
  }
  h += '</tbody></table>';
  $('#cmp-head').innerHTML = h;
}
function renderGrid(a, b){
  const A = D.data[a], B = D.data[b];
  let h = '';
  for (const cat of D.cats){
    h += '<div class="cmp-cat"><div class="cmp-cath">'+cat.key+'</div>';
    for (const tid of cat.tids){
      const va = A.t[tid] ?? null, vb = B.t[tid] ?? null;
      const A1 = sc(va), B1 = sc(vb);
      let d = '';
      if (va!==null && vb!==null && Math.abs(va-vb) > 1e-9){
        const diff = va - vb;
        d = '<span class="cmp-td '+(diff>0?'ga':'gb')+'">'
          + (diff>0?'\\u25c0 ':'') + (diff>0?'+':'') + diff.toFixed(3)
          + (diff<0?' \\u25b6':'') + '</span>';
      } else if (va!==null && vb!==null){ d = '<span class="cmp-td tie">=</span>'; }
      h += '<div class="cmp-row">'
         + '<a class="cmp-t" href="tasks/'+tid+'.html">'+tid+'</a>'
         + '<span class="scv '+A1.cls+' ra">'+A1.txt+A1.sw+'</span>'
         + '<span class="cmp-dc">'+d+'</span>'
         + '<span class="scv '+B1.cls+'">'+B1.sw+'<b>'+B1.txt+'</b></span>'
         + '</div>';
    }
    h += '</div>';
  }
  $('#cmp-grid').innerHTML = h;
}
function render(){
  const a = $('#selA').value, b = $('#selB').value;
  renderHead(a, b); renderGrid(a, b);
  const u = new URL(location); u.searchParams.set('a',a); u.searchParams.set('b',b);
  history.replaceState(null,'',u);
}
(function init(){
  const opts = D.models.map(m => '<option value="'+m+'">'+m+'</option>').join('');
  $('#selA').innerHTML = opts; $('#selB').innerHTML = opts;
  const p = new URLSearchParams(location.search);
  $('#selA').value = p.get('a') && D.data[p.get('a')] ? p.get('a') : D.models[0];
  $('#selB').value = p.get('b') && D.data[p.get('b')] ? p.get('b')
                   : (D.models[1] || D.models[0]);
  $('#selA').onchange = render; $('#selB').onchange = render;
  $('#swap').onclick = () => { const t=$('#selA').value;
    $('#selA').value=$('#selB').value; $('#selB').value=t; render(); };
  render();
})();
</script>
</body></html>"""


def build_feed(runs: list[dict], tdefs: dict) -> str:
    """Atom feed of 'model first tested' events, newest first (G6 freshness).

    Every entry's date is a RUN date, not the wall clock, so the feed is a pure
    function of the data: it only changes when a new model actually lands, and
    the shipped reports stay byte-stable between publishes. That is also the
    honest 'last updated' for a benchmark — when the data moved, not when the
    generator last ran."""
    from xml.sax.saxutils import escape

    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}

    first_seen: dict[str, str] = {}
    for r in sorted(runs, key=lambda r: r["run_id"]):
        started = r["manifest"].get("started") or r["run_id"]
        for res in r["results"]:
            first_seen.setdefault(res["model"], started)

    def _score(m):
        xs = [e["score"]["score"] for info in task_data.values()
              if (e := info["agg"].get(m))
              and e["score"].get("status") == "scored"
              and e["score"].get("score") is not None]
        return sum(xs) / len(xs) if xs else None

    events = sorted(first_seen.items(), key=lambda kv: kv[1], reverse=True)
    updated = events[0][1] if events else "1970-01-01T00:00:00Z"
    site = "https://tokenwaster.github.io/llm-testing-public"
    ver = config.suite_version()

    entries = []
    for m, when in events:
        sc = _score(m)
        summ = (f"{m} entered the benchmark. Mean score {sc:.3f} across the "
                f"suite (v{ver})." if sc is not None
                else f"{m} entered the benchmark (v{ver}).")
        entries.append(
            f"  <entry>\n"
            f"    <title>{escape(m)} added to the benchmark</title>\n"
            f"    <id>tag:llm-testing,{when[:10]}:{escape(m)}</id>\n"
            f"    <updated>{escape(when)}</updated>\n"
            f"    <link href=\"{site}/reports/models/{_slug_name(m)}.html\"/>\n"
            f"    <summary>{escape(summ)}</summary>\n"
            f"  </entry>")

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        '  <title>LLM Testing — models tested</title>\n'
        f'  <id>tag:llm-testing,2026:feed</id>\n'
        f'  <updated>{escape(updated)}</updated>\n'
        f'  <link href="{site}/reports/index.html"/>\n'
        f'  <link rel="self" href="{site}/reports/feed.xml"/>\n'
        + "\n".join(entries) + "\n</feed>\n")


def build_compare_page(runs: list[dict], tdefs: dict, dataset_label: str = "",
                       dataset_key: str = "live") -> str:
    """Head-to-head: pick any two models, see every task side by side.

    All the per-model, per-task numbers are embedded once as JSON and the page
    renders client-side, so a static host needs no server — the two dropdowns
    just re-read the blob. Scores are the same aggregated means the leaderboard
    uses, and the swatch ramp mirrors the overview matrix so a cell reads the
    same everywhere."""
    import json as _json

    _, hidden = _model_prefs()
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    by_model: dict[str, list] = {}
    for tid, info in task_data.items():
        for m, e in info["agg"].items():
            if m not in hidden:
                by_model.setdefault(m, []).append(e)
    summaries = {m: _summarize(rs) for m, rs in by_model.items()}

    ranked = sorted(summaries, key=lambda m: (
        -(summaries[m]["avg_score_val"]
          if summaries[m]["avg_score_val"] is not None else -1.0), m))
    rank_of = {m: i + 1 for i, m in enumerate(ranked)}

    def _score_on(m, tid):
        e = task_data[tid]["agg"].get(m)
        if e and e["score"].get("status") == "scored" \
                and e["score"].get("score") is not None:
            return round(e["score"]["score"], 6)
        return None

    data = {}
    for m in ranked:
        s = summaries[m]
        graded = sum(1 for tid in task_data
                     if _score_on(m, tid) is not None)
        npass = sum(1 for tid in task_data
                    if (v := _score_on(m, tid)) is not None and v >= 0.8)
        data[m] = {
            "slug": _slug_name(m),
            "rank": rank_of[m],
            "where": "local" if s["local"] else "cloud / CLI",
            "score": (round(s["avg_score_val"], 6)
                      if s["avg_score_val"] is not None else None),
            "ci": (round(s["score_ci95"], 6)
                   if s.get("score_ci95") is not None else None),
            "pass": npass, "graded": graded,
            "costVal": round(s["cost_val"], 6) if s.get("cost_val") else 0,
            "costStr": s["cost"],
            "tps": (float(s["tps"]) if s["tps"] not in ("—", None) else None),
            "wall": s["wall_ms_sum"],
            "timeStr": fmt_span(s["wall_ms_sum"]),
            "ft": s.get("first_try_val"),
            "t": {tid: _score_on(m, tid) for tid in task_data},
        }

    cats: dict[str, list] = {}
    for tid in task_data:
        cats.setdefault(tdefs[tid].category, []).append(tid)
    cat_list = [{"key": c, "tids": sorted(cats[c])} for c in sorted(cats)]

    payload = {"models": ranked, "data": data, "cats": cat_list}
    data_json = _json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    return _env.from_string(COMPARE_TEMPLATE).render(
        nav=_nav(""), css=BASE_CSS, data_json=data_json,
        dataset_label=dataset_label, dataset_key=dataset_key)


def generate_all(runs_dir: Path | None = None, out_dir: Path | None = None,
                 dataset_label: str = "", dataset_key: str = "live",
                 tasks_dir: Path | None = None, public_nav: bool = False) -> Path:
    """Render a complete report site for one dataset. Defaults to live runs/ +
    current tasks; archive.render_dataset points it at an archived snapshot.
    `public_nav=True` drops the operator-only control links (public export)."""
    global _RUNS_BASE, _PUBLIC_NAV
    runs_dir = runs_dir or config.RUNS_DIR
    out_dir = out_dir or config.REPORTS_DIR
    prev_base, prev_public = _RUNS_BASE, _PUBLIC_NAV
    _RUNS_BASE = runs_dir
    _PUBLIC_NAV = public_nav
    try:
        runs = load_all_runs(runs_dir)
        tdefs = _task_defs(tasks_dir)
        from .util import strip_output_comments
        def _w(path, html):
            path.write_text(strip_output_comments(html), encoding="utf-8")
        out_runs = out_dir / "runs"
        out_runs.mkdir(parents=True, exist_ok=True)
        for stale in out_runs.glob("*.html"):
            stale.unlink()
        for r in runs:
            _w(out_runs / f"{r['run_id']}.html", build_run_report(r, tdefs))
        out_tasks = out_dir / "tasks"
        out_tasks.mkdir(parents=True, exist_ok=True)
        for stale in out_tasks.glob("*.html"):
            stale.unlink()
        from . import assess
        _acfg = assess.load_cfg()
        _tdata = collect_task_data(runs)
        _suspect = assess.suspect_answers(_tdata, tdefs, _acfg)
        for tid, info in _tdata.items():
            if tid not in tdefs:
                continue
            _w(out_tasks / f"{tid}.html",
               build_task_report(tid, info, tdefs.get(tid), _acfg, _suspect))
        out_models = out_dir / "models"
        out_models.mkdir(parents=True, exist_ok=True)
        for stale in out_models.glob("*.html"):
            stale.unlink()
        _, hidden = _model_prefs()
        seen_models = sorted({res["model"] for r in runs
                              for res in r["results"]} - hidden)
        versions = load_versions() if dataset_key == "live" else None
        for m in seen_models:
            _w(out_models / f"{_slug_name(m)}.html",
               build_model_report(m, runs, tdefs, dataset_label, versions))
        _w(out_dir / "info.html",
           build_info_page(runs, tdefs, dataset_label, dataset_key))
        _w(out_dir / "discriminate.html",
           build_discriminate_page(runs, tdefs, dataset_label, dataset_key))
        _w(out_dir / "family.html",
           build_family_page(runs, tdefs, dataset_label, dataset_key, versions))
        _w(out_dir / "compare.html",
           build_compare_page(runs, tdefs, dataset_label, dataset_key))
        if dataset_key == "live":
            _w(out_dir / "feed.xml", build_feed(runs, tdefs))
        index = out_dir / "index.html"
        _w(index, build_index(runs, tasks_dir=tasks_dir,
                              dataset_label=dataset_label, dataset_key=dataset_key,
                              versions=versions))
        return index
    finally:
        _RUNS_BASE = prev_base
        _PUBLIC_NAV = prev_public
