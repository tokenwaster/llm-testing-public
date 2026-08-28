
import html as _html
import threading
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
_LIVE_ONLY = {"special.html", "links.html"}
_DATASET_KEY = "live"

_NAV = [
    ("Overview", "index.html", False), ("Families", "family.html", False),
    ("Discriminate", "discriminate.html", False),
    ("Compare", "compare.html", False),
    ("Run", "/run", True), ("Watch", "/watch", True),
    ("Review", "/review", True),
    ("Backend", "/backend", True), ("Manage data", "/manage", True),
    ("Organize", "/families-edit", True),
    ("Mirror", "/mirror", True),
    ("Special", "special.html", False),
    ("Info", "info.html", False),
]


BRAND_NAME = "Token Waster"

BRAND_SVG = (
    '<svg viewBox="0 0 32 32" role="img" aria-label="Token Waster" '
    'fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="2.5"/>'
    '<path d="M9.5 22.5 L22.5 9.5" stroke="currentColor" stroke-width="2.5" '
    'stroke-linecap="round"/>'
    '</svg>')


def _brand(prefix: str = "") -> str:
    return (f'<a class="brand" href="{prefix}index.html" '
            f'title="{BRAND_NAME}">{BRAND_SVG}'
            f'<span class="bw">{BRAND_NAME}</span></a>')


SOCIALS = [
    ("YouTube", "https://www.youtube.com/@TokenWaster", "#FF0000",
     "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545"
     "s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93."
     "502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505"
     " 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-."
     "502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"),
    ("X", "https://x.com/tokenwaster", "#000000",
     "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258"
     " 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3"
     ".182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"),
    ("TikTok", "https://www.tiktok.com/@tokenwaster", "#000000",
     "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 "
     "2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-."
     "93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17"
     "-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5"
     "-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72."
     "02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 "
     "1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66"
     " 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02"
     "-12.07z"),
    ("Instagram", "https://www.instagram.com/tokenwaster/", "#E4405F",
     "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228"
     " 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 "
     "2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 "
     "4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228."
     "6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773"
     ".056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-."
     "0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682"
     " 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809."
     "0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-."
     "264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 "
     "20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 "
     "15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1."
     "17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-."
     "4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645"
     "-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1."
     "805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-."
     "9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 "
     "3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608."
     "216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056"
     ".4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061"
     " 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-."
     "419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595"
     "-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44"
     " 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 "
     "3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-."
     "0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738"
     "M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"),
    ("GitHub", "https://github.com/tokenwaster", "#181717",
     "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-."
     "258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422"
     " 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 "
     "1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1."
     "605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-."
     "54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02."
     "006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 "
     "3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 "
     "1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 "
     "22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"),
]


def _social_rail() -> str:
    items = "".join(
        f'<a class="sr-i" href="{url}" target="_blank" rel="noopener me" '
        f'title="{name}" aria-label="{name}" style="--brand:{colour}">'
        f'<svg viewBox="0 0 24 24" aria-hidden="true">'
        f'<path fill="currentColor" d="{path}"/></svg></a>'
        for name, url, colour, path in SOCIALS)
    return f'<nav class="srail" aria-label="Social links">{items}</nav>'


def _nav(prefix: str = "") -> str:
    out = []
    for label, href, control in _NAV:
        if control and _PUBLIC_NAV:
            continue
        if href in _LIVE_ONLY and _DATASET_KEY != "live":
            continue
        target = href if control else prefix + href
        if label == "Special" and not _PUBLIC_NAV:
            target = "/special"
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


_GEN_CACHE: dict | None = None


def _gen_cached(key, build):
    if _GEN_CACHE is None:
        return build()
    if key not in _GEN_CACHE:
        _GEN_CACHE[key] = build()
    return _GEN_CACHE[key]


def load_all_runs(runs_dir: Path | None = None) -> list[dict]:
    runs_dir = runs_dir or config.RUNS_DIR
    if not runs_dir.exists():
        return []

    def build():
        from .tasks import load_tasks
        staged = {t.id for t in load_tasks(include_staging=True) if t.staging}
        runs = [load_run(d) for d in sorted(runs_dir.iterdir()) if d.is_dir()]
        out = []
        for r in runs:
            if not r:
                continue
            if staged:
                r["results"] = [res for res in r["results"]
                                if res.get("task") not in staged]
            if r["results"]:
                out.append(r)
        return out

    return _gen_cached(("runs", str(runs_dir.resolve())), build)


def _cached_tasks(tasks_dir: Path | None = None) -> list:
    from .tasks import load_tasks
    key = ("tasks", str((tasks_dir or config.TASKS_DIR).resolve()))
    return _gen_cached(key, lambda: load_tasks(tasks_dir))




def forecast_accuracy(runs: list[dict] | None = None) -> dict:
    runs = load_all_runs() if runs is None else runs
    rows = []
    for r in runs:
        mani = r["manifest"] or {}
        fc = mani.get("cost_forecast")
        if not fc or not fc.get("billable"):
            continue
        cut_short = bool(mani.get("stopped_reason"))
        billed = {}
        source = {}
        for res in r["results"]:
            c = res.get("cost_usd")
            if c is None:
                continue
            billed[res["model"]] = billed.get(res["model"], 0.0) + c
            if res.get("cost_source") == "billed":
                source[res["model"]] = True
        per = []
        for m in fc.get("models") or []:
            act = billed.get(m["model"])
            if act is None or not m.get("total"):
                continue
            per.append({
                "model": m["model"], "basis": m.get("basis"),
                "measured": m.get("priced"), "of": m.get("tasks"),
                "estimate": m["total"], "actual": round(act, 6),
                "err_pct": round((act - m["total"]) / m["total"] * 100, 1),
                "receipted": bool(source.get(m["model"])),
            })
        if not per:
            continue
        est = sum(p["estimate"] for p in per)
        act = sum(p["actual"] for p in per)
        rows.append({
            "run_id": r["run_id"],
            "cut_short": cut_short,
            "stopped_reason": mani.get("stopped_reason"),
            "started": (r["manifest"] or {}).get("started", ""),
            "estimate": round(est, 6), "actual": round(act, 6),
            "err_pct": round((act - est) / est * 100, 1) if est else None,
            "cap": fc.get("cap"),
            "models": per,
        })
    rows.sort(key=lambda r: r["started"])
    errs = [r["err_pct"] for r in rows
            if r["err_pct"] is not None and not r["cut_short"]]
    over = [e for e in errs if e < 0]
    summary = None
    if errs:
        import statistics as _st
        summary = {
            "n_runs": len(errs),
            "n_cut_short": sum(1 for r in rows if r["cut_short"]),
            "median_err_pct": round(_st.median(errs), 1),
            "worst_over_pct": round(min(errs), 1),
            "worst_under_pct": round(max(errs), 1),
            "conservative_share": round(len(over) / len(errs), 3),
            "total_estimate": round(sum(r["estimate"] for r in rows
                                       if not r["cut_short"]), 4),
            "total_actual": round(sum(r["actual"] for r in rows
                                     if not r["cut_short"]), 4),
        }
    return {"rows": rows, "summary": summary}


def fmt_ms(ms) -> str:
    if ms is None:
        return "—"
    return f"{ms / 1000:.1f}s" if ms >= 1000 else f"{ms:.0f}ms"


def fmt_span(ms) -> str:
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
    events = read_jsonl(_RUNS_BASE / run_id / model / task / "transcript.jsonl")
    text = ""
    for ev in events:
        if ev.get("event") == "response" and ev.get("text"):
            text = ev["text"]
    if len(text) > limit:
        text = text[:limit] + f"\n…[truncated, {len(text) - limit} more chars in transcript]"
    return text


def score_state(s: dict) -> str:
    if not s or s.get("status") != "scored" or s.get("score") is None:
        return "pend"
    v = s["score"]
    return "good" if v >= 0.8 else ("warn" if v >= 0.4 else "crit")


CHIP_SYMBOL = {"good": "✓", "warn": "◐", "crit": "✕", "pend": "◌"}


def chip(state: str, text: str, tip: str = "") -> str:
    return (f'<span class="chip {state}" title="{html.escape(tip)}">'
            f'<i>{CHIP_SYMBOL[state]}</i>{html.escape(text)}</span>')


def _heat_swatch(v: float | None) -> str:
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
    "repetition_loop": ("↻ loop", "#b59"),
    "runaway": ("⟳ runaway", "#c90"),
    "timeout": ("⧖ timeout", "#c60"),
    "max_turns": ("⇥ max-turns", "#96c"),
    "endpoint": ("⛔ endpoint", "#c33"),
    "error": ("⚠ error", "#c33"),
}


def _failure_mode_of(e: dict) -> str | None:
    fm = e.get("failure_mode")
    if fm:
        return fm
    if e.get("status") == "max_turns":
        return "max_turns"
    atts = e.get("attempts") or []
    if not atts:
        return None
    last = atts[-1]
    if last.get("error_kind") == "repetition_loop":
        return "repetition_loop"
    if last.get("error_kind") == "runaway":
        return "runaway"
    sc = e.get("score") or {}
    failed = sc.get("status") != "scored" or (sc.get("score") or 0) == 0
    if last.get("stop_reason") == "length" and failed:
        return "runaway"
    if last.get("error_kind") in ("timeout", "rumination_spiral"):
        return "timeout"
    if last.get("error_kind"):
        if any(attempt_blame(a) == "endpoint" for a in atts):
            return "endpoint"
        return "error"
    return None


def _fail_badge(e: dict) -> str:
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
    if not tdef:
        return None
    from . import assess
    cls = assess.classify(e, tdef, acfg or assess.load_cfg(), suspect)
    return None if cls["category"] == "pass" else cls


def why_cell(cls: dict | None) -> str:
    if not cls:
        return ""
    attr = cls["attribution"]
    cat = cls["category"].replace("-", " ")
    return (f'<span class="attr attr-{attr}">{attr}</span> '
            f'<span title="{html.escape(cls["detail"])}">{html.escape(cat)}</span>')


def sparkline(values: list[float | None], width=140, height=34) -> str:
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
    import re
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-").lower() or "model"


def _mlink(name: str, prefix: str = "", cls: str = "mlink") -> str:
    return (f'<a class="{cls}" href="{prefix}models/{_slug_name(name)}.html">'
            f'{html.escape(name)}</a>')


def chart_legend(entries: list[dict], prefix: str = "") -> str:
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
    import math
    if v <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return m * mag
    return 10 * mag


def scatter(points: list[dict], width=1000, height=340) -> str:
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
    xb = (q["x"] <= p["x"]) if x_minimize else (q["x"] >= p["x"])
    xs = (q["x"] < p["x"]) if x_minimize else (q["x"] > p["x"])
    return xb and q["y"] >= p["y"] and (xs or q["y"] > p["y"])


def pareto_scatter(points: list[dict], x_label: str, *, x_minimize: bool,
                   x_fmt: str = "{:,.2f}", width: int = 1000,
                   height: int = 360) -> str:
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
  --hair:rgba(255,255,255,.07); --rule:rgba(255,255,255,.15);
  --trap:#ffd60a; --miss:#d9600f; --cell-rgb:242,242,240;
  --cell-ink:#0b0b0b;
  --mono:ui-monospace,"Cascadia Code","JetBrains Mono","SF Mono",Menlo,Consolas,monospace;
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
    --trap:#a87f00; --miss:#b8460a; --cell-rgb:22,22,26;
    --cell-ink:#ffffff;
    --s1:#2a78d6; --s2:#1baf7a; --s3:#eda100; --s4:#008300;
    --s5:#4a3aa7; --s6:#e34948; --s7:#e87ba4; --s8:#eb6834;
    color-scheme: light;
  }
}
* { box-sizing:border-box; }
body { background:var(--plane); color:var(--ink);
  font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
h1 { font-size:21px; font-weight:650; letter-spacing:-.01em; margin:0; }
.sub { color:var(--muted); font-size:12.5px; margin-top:4px; }
.reflink { display:inline-block; margin-left:10px; padding:1px 7px; border-radius:10px;
  border:1px solid var(--border); font-size:11.5px; text-decoration:none; white-space:nowrap; }
.reflink:hover { border-color:var(--accent); color:var(--accent); }
__HEADER_CSS__
.tag.lens-hard { background:transparent; color:var(--warn);
  border:1px solid var(--warn); }
.tag.lens-frontier { background:transparent; color:var(--crit);
  border:1px solid var(--crit); }
.tag.lens-easy, .tag.lens-mid { background:transparent; color:var(--muted);
  border:1px solid var(--hair); }
.tag { display:inline-block; background:var(--accent-soft); color:var(--accent);
  border-radius:20px; padding:2px 11px; font-size:11.5px; font-weight:600;
  margin-left:10px; vertical-align:2px; }
h2 { font-family:var(--mono); font-size:10.5px; font-weight:600; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); margin:34px 0 10px; }

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

.card, .vc-cats, .vc-members, .vc-catdet {
  background:var(--surface); border:1px solid var(--hair);
  border-radius:6px; padding:2px 0; overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:13px;
  font-variant-numeric:tabular-nums; }
th { color:var(--muted); font-family:var(--mono); font-size:10px; font-weight:600;
  letter-spacing:.1em; text-transform:uppercase; text-align:left; padding:10px 14px 8px;
  border-bottom:1px solid var(--rule); white-space:nowrap; }
td { padding:8px 14px; border-bottom:1px solid var(--hair); vertical-align:middle; }
tr:last-child td { border-bottom:none; }
tbody tr:hover td { background:var(--surface-2); }
td.num, th.num, th[data-type="num"] { text-align:center; font-variant-numeric:tabular-nums; }
td.num.warn { color:var(--warn); font-weight:650; }
th[data-type="text"], td.model { text-align:left; }
td.nowrap, .nowrap { white-space:nowrap; }
.model { font-weight:600; }
.muted { color:var(--muted); }
th.lenscol, td.lensval { background:var(--accent-soft); font-weight:600; }
.chartkey { display:flex; flex-wrap:wrap; align-items:center; gap:6px 16px;
  font-size:12px; color:var(--ink-dim); margin:2px 0 6px; }
.chartkey .k-dot { display:inline-block; width:10px; height:10px; border-radius:50%;
  background:var(--accent); vertical-align:-1px; margin-right:2px; }
.chartkey .k-dot.dim { opacity:.4; }
.chartkey .k-line { display:inline-block; width:26px; border-top:2px dashed var(--accent);
  vertical-align:4px; margin:0 2px 0 6px; }
.tiepop { display:inline-block; vertical-align:baseline; }
.tiepop > summary { display:inline; cursor:help; list-style:none;
  color:var(--muted); font-size:12px; border-bottom:1px dotted var(--muted); }
.tiepop > summary::-webkit-details-marker { display:none; }
.tiepop > summary::after { content:" ▸"; font-size:9px; }
.tiepop[open] > summary::after { content:" ▾"; }
.tiepop > summary:hover { color:var(--accent); border-bottom-color:var(--accent); }
.tiepop .tp-list { display:flex; flex-direction:column; gap:2px; margin:6px 0 2px;
  padding:7px 10px; max-height:280px; overflow-y:auto; font-size:12.5px;
  background:var(--surface-2); border:1px solid var(--hair); border-radius:6px; }
.szttip { position:fixed; z-index:60; pointer-events:none; display:none;
  background:var(--surface); border:1px solid var(--border); border-radius:8px;
  padding:6px 9px; font-size:12px; line-height:1.5; color:var(--ink);
  box-shadow:0 6px 20px rgba(0,0,0,.35); max-width:300px; }
.szttip b { color:var(--ink); }
table.sortable th[data-type] { cursor:pointer; user-select:none; white-space:nowrap; }
table.sortable th[data-type]:hover { color:var(--ink); }
table.sortable th .caret { opacity:0; font-size:9px; margin-left:5px;
  vertical-align:1px; }
table.sortable th[data-type]:hover .caret { opacity:.4; }
table.sortable th.sorted .caret { opacity:1; color:var(--accent); }
.fitpick { font-weight:650; color:var(--good); white-space:nowrap; }
.fitval { font-weight:600; color:var(--accent); white-space:nowrap; }
.small { font-size:11.5px; color:var(--muted); }
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
a.mlink { color:inherit; font-weight:600; text-decoration:none;
  border-bottom:1px dotted var(--border); }
a.mlink:hover { color:var(--accent); border-bottom-color:var(--accent);
  text-decoration:none; }

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

.scv { display:inline-flex; align-items:center; font-variant-numeric:tabular-nums;
  white-space:nowrap; }
.scv b { font-weight:600; }
.scv.warn b { color:var(--warn); }
.scv.crit b { color:var(--crit); }
.scv.pend { color:var(--muted); font-weight:500; }
.hsw { display:inline-block; width:11px; height:11px; border-radius:2px; flex:none;
  margin-right:7px; background:rgba(var(--cell-rgb),var(--a,.2)); }
.hsw.pend { background:transparent; box-shadow:inset 0 0 0 1px var(--hair); }
.cmp-pick { display:grid; grid-template-columns:minmax(150px,1fr) 1fr 84px 1fr;
  align-items:center; gap:0; margin:6px 0 22px; }
.cmp-sel { min-width:0; width:100%; font-size:15px; font-weight:600;
  padding:9px 12px; border-radius:8px; border:1px solid var(--border);
  background:var(--surface); color:var(--ink); font-family:inherit; }
.cmp-swap { justify-self:center; font-size:18px; line-height:1; padding:8px 12px; cursor:pointer;
  border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--ink); }
@media (max-width:760px) {
  .cmp-pick { grid-template-columns:1fr; gap:10px; }
  .cmp-pick .cmp-lead { display:none; }
  .cmp-swap { justify-self:start; }
}
.cmp-swap:hover { border-color:var(--accent); color:var(--accent); }
.cmp-head { margin:0 0 28px; overflow-x:auto; }
.cmp-hrow { border-bottom:1px solid var(--rule); align-items:end;
  padding-bottom:8px; margin-bottom:2px; }
.cmp-hc { text-align:center; font-size:15px; font-weight:700; }
.cmp-hc a { font-weight:700; }
.cmp-hc .small { font-weight:400; }
.cmp-k { text-align:left; font-family:var(--mono); font-size:11px;
  letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
  align-self:center; padding-right:10px; }
.cmp-v { text-align:center; font-variant-numeric:tabular-nums; font-size:14px; }
.cmp-v.win { color:var(--good); font-weight:750; }
.cmp-cat { margin:0 0 18px; }
.cmp-cath { font-family:var(--mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); padding:6px 0 4px; border-bottom:1px solid var(--rule); margin-bottom:4px; }
.cmp-row { display:grid; grid-template-columns:minmax(150px,1fr) 1fr 84px 1fr;
  align-items:center; gap:0; padding:3px 0; border-bottom:1px solid var(--hair); }
.cmp-row:hover { background:var(--surface); }
.cmp-t { font-size:12.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  padding-right:10px; }
.cmp-row .scv { justify-content:center; font-variant-numeric:tabular-nums; }
.cmp-row .scv.ra .hsw { margin-right:0; margin-left:7px; }
.cmp-dc { text-align:center; align-self:stretch; display:flex; align-items:center;
  justify-content:center;
  background:linear-gradient(var(--rule),var(--rule)) center/2px 100% no-repeat; }
.cmp-td { font-family:var(--mono); font-size:11px; white-space:nowrap;
  padding:0 5px; background:var(--plane); }
.cmp-td.ga { color:var(--good); } .cmp-td.gb { color:var(--accent); }
.cmp-td.tie { color:var(--muted); }

.spark path { fill:none; stroke:var(--accent); stroke-width:2;
  stroke-linecap:round; stroke-linejoin:round; }
.spark circle { fill:var(--accent); }
.spark .axis { stroke:var(--grid); stroke-width:1; }
.track { display:inline-block; height:8px; background:var(--surface-2);
  border-radius:4px; vertical-align:middle; overflow:hidden; }
.fill { display:block; height:8px; background:var(--accent);
  border-radius:0 4px 4px 0; }

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
@media (max-width:760px) {
  h1 { font-size:19px; }
  .topbar { flex-direction:column; align-items:flex-start; gap:8px; }
  .nav { display:flex; flex-wrap:wrap; row-gap:4px; }
  .nav a { margin-left:0; margin-right:15px; }
  table { display:block; overflow-x:auto; -webkit-overflow-scrolling:touch;
    max-width:100%; }
}

.grid, .scatter .grid { stroke:var(--grid); stroke-width:1; }
.tick, .scatter .tick { fill:var(--muted); font-size:10px;
  font-variant-numeric:tabular-nums; }

.bump .bm { transition:opacity .1s; }
.bump .bmhit, .bump .bmlabel { cursor:pointer; }
.bump.focus .bm { opacity:.12; }
.bump.focus .bm.on { opacity:1; }

.dot .hit { fill:transparent; }
.dot .mk { stroke:var(--surface); stroke-width:2; transition:opacity .1s; }
.dot:hover .mk { stroke:var(--ink); stroke-width:2.5; }
.chartwrap.focus .dot .mk { opacity:.13; }
.chartwrap.focus .dot.on .mk { opacity:1; }
.clegend.focus .cl-item { opacity:.35; }
.clegend.focus .cl-item.on { opacity:1; }

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
details.det.hit { border-color:var(--accent); box-shadow:0 0 0 1px var(--accent); }
tr.hit > td { background:var(--surface); }
tr.hit > td:first-child { box-shadow:inset 2px 0 0 var(--accent); }
a.filelink { font-family:var(--mono); font-size:11px; color:var(--muted);
  border:1px solid var(--hair); border-radius:4px; padding:2px 6px; white-space:nowrap; }
a.filelink:hover { color:var(--accent); border-color:var(--accent); }
.sig { font-family:var(--mono); font-size:10px; color:var(--muted); margin-left:5px; }
.nrun { font-family:var(--mono); font-size:10px; color:var(--accent);
  border:1px solid var(--hair); border-radius:3px; padding:0 3px; cursor:help; }
.snote { display:block; font-family:var(--mono); font-size:9.5px; color:var(--muted);
  letter-spacing:.03em; }
.hardmark { color:var(--accent); }
.vc-pick { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:10px; font-size:12px;
  color:var(--muted); align-items:center; }
.vc-pick select { background:var(--plane); color:var(--fg); border:1px solid var(--grid);
  border-radius:5px; padding:3px 7px; font-size:12px; margin-left:4px; }
.vc-sum { font-size:13.5px; margin:4px 0 14px; }
.vc-cell { display:inline-block; min-width:36px; text-align:center; font-family:var(--mono);
  font-size:11px; border-radius:3px; padding:2px 4px; margin-right:3px;
  border:1px solid var(--hair); color:var(--ink); }
.vc-cell.flip-d { color:var(--cell-ink); }
@media (prefers-color-scheme: light) {
  .vc-cell.flip-d { color:var(--ink); }
  .vc-cell.flip-l { color:var(--cell-ink); }
}
.vc-d { font-family:var(--mono); font-size:11px; font-weight:600; padding:1px 5px;
  border-radius:3px; margin:0 8px; }
.vc-d.up { color:#1f9d55; } .vc-d.down { color:var(--crit); } .vc-d.flat { color:var(--muted); }
.vc-verd { font-size:10px; text-transform:uppercase; letter-spacing:.05em; padding:1px 6px;
  border-radius:3px; border:1px solid var(--hair); }
.vc-verd.better { color:#1f9d55; border-color:#1f9d55; }
.vc-verd.worse { color:var(--crit); border-color:var(--crit); }
.vc-catrow, .vc-taskrow { display:flex; align-items:center; gap:2px;
  padding:8px 14px; font-size:12px; border-bottom:1px solid var(--hair); }
.vc-catrow:last-child, .vc-taskrow:last-child { border-bottom:none; }
.vc-catrow:hover, .vc-taskrow:hover { background:var(--surface-2); }
.vc-cat { min-width:130px; color:var(--muted); font-size:11px; }
.vc-cats, .vc-members, .vc-catdet { margin:8px 0 4px; }
.vc-catdet > summary { cursor:pointer; padding:8px 14px; color:var(--ink-2);
  font-size:12px; list-style:none; border-bottom:1px solid var(--hair); }
.vc-catdet:not([open]) > summary { border-bottom:none; }
.vc-catdet > summary::before { content:"›"; color:var(--muted); margin-right:6px; }
.vc-catdet[open] > summary::before { content:"⌄"; }
.vc-wrap { padding:12px 14px; }
.vc-note { color:var(--muted); font-size:11px; margin:0; }
p.vc-note { margin:8px 0 0; }
.vc-warn { color:var(--trap); font-size:10px; margin-left:6px; }
pre { background:var(--plane); border:1px solid var(--grid); padding:10px 12px;
  border-radius:8px; font-size:12px; overflow-x:auto; white-space:pre-wrap;
  color:var(--ink-2); }
.foot { margin-top:36px; font-size:11.5px; color:var(--muted); line-height:1.7;
  border-top:1px solid var(--grid); padding-top:14px; }
code { background:var(--surface-2); border-radius:4px; padding:1px 6px;
  font-size:12px; }
"""

HEADER_CSS = """
:root { --topbar-h:56px; --brand-h:32px; --shell-w:1480px; --shell-x:30px; }
body { max-width:var(--shell-w); margin:0 auto;
  padding:32px var(--shell-x) 72px; }
@media (max-width:760px) {
  body { padding:20px 15px 56px; }
}
.topbar { display:flex; align-items:center; justify-content:space-between;
  gap:20px; flex-wrap:nowrap; height:var(--topbar-h); margin:0 0 18px;
  border-bottom:1px solid var(--hair); }
.brand { flex:none; display:flex; align-items:center; gap:11px;
  height:var(--brand-h); text-decoration:none; color:var(--ink); }
.brand:hover { text-decoration:none; }
.brand svg, .brand img { height:var(--brand-h); width:auto; display:block;
  flex:none; }
.brand .bw { font-weight:700; font-size:15px; letter-spacing:-.01em;
  white-space:nowrap; }
.topbar .ttl { flex:1 1 auto; min-width:0; display:flex; align-items:center;
  gap:10px; }
.topbar h1 { font-size:18px; font-weight:650; letter-spacing:-.01em; margin:0;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.topbar .nav { flex:none; display:block; margin:0; white-space:nowrap; }
.topbar .nav a { margin:0 0 0 16px; font-size:13px; color:var(--accent);
  text-decoration:none; }
.topbar .nav a:hover { text-decoration:underline; }
@media (max-width:1080px) {
  :root { --topbar-h:auto; }
  .topbar { flex-wrap:wrap; height:auto; min-height:56px; padding-bottom:10px;
    align-items:center; row-gap:8px; }
  .topbar .nav { flex:1 0 100%; overflow-x:auto; scrollbar-width:none; }
  .topbar .nav::-webkit-scrollbar { display:none; }
  .topbar .nav a { margin:0 16px 0 0; }
}
.pagebar { display:flex; align-items:center; gap:12px; flex-wrap:wrap;
  margin:0 0 20px; font-size:12.5px; color:var(--muted); }
.pagebar .sub { margin:0; }
.srail { position:fixed; z-index:30; top:50%; transform:translateY(-50%);
  right:calc((100vw - var(--shell-w)) / 2 - 52px);
  display:flex; flex-direction:column; gap:6px;
  padding:7px 6px; border-radius:12px;
  background:var(--surface); border:1px solid var(--hair); }
.srail .sr-i { display:flex; align-items:center; justify-content:center;
  width:30px; height:30px; border-radius:8px; color:var(--muted);
  text-decoration:none; }
.srail .sr-i svg { width:17px; height:17px; display:block; }
.srail .sr-i:hover { color:var(--brand); background:var(--surface-2);
  text-decoration:none; }
@media (prefers-color-scheme: dark) {
  .srail .sr-i[title="X"]:hover, .srail .sr-i[title="GitHub"]:hover {
    color:var(--ink); }
}
@media (max-width:1609px) {
  .srail { top:auto; bottom:18px; right:18px; transform:none;
    flex-direction:row; box-shadow:0 4px 18px rgba(0,0,0,.28); }
}
@media (max-width:760px) {
  .srail { bottom:12px; right:12px; gap:2px; padding:5px 4px; }
  .srail .sr-i { width:28px; height:28px; }
}
@media print { .srail { display:none; } }
"""

BASE_CSS = BASE_CSS.replace("__HEADER_CSS__", HEADER_CSS)

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
.mx-row.partial .mx-rail { opacity:.62; }
.mx-row.partial .pcov { font-size:9.5px; padding:0 4px; border-radius:6px;
  border:1px solid var(--warn); color:var(--warn); vertical-align:middle; }
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
<div class="topbar">{{ brand }}<div class="ttl"><h1>Run {{ run_id }}{% if manifest.tag %}<span class="tag">{{ manifest.tag }}</span>{% endif %}</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">{{ manifest.started }} → {{ manifest.finished or "…" }}{% if env_line %} · {{ env_line }}{% endif %}</div></div>

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

<div class="foot">{{ cost_note|safe }}</div>
<div class="foot">Wall times include every retry. Token counts come from each
provider's usage field — never estimated. Gen tok/s = completion tokens ÷
generation time (excludes time-to-first-token).</div>
{{ sort_js }}
</body></html>"""

TASK_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ task_id }} · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>{{ title }}<span class="tag">{{ category }} · tier {{ tier }}</span>{% if lens %}<span class="tag lens-{{ lens.key }}" title="{{ lens.why }}">{{ lens.label }}</span>{% endif %}</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">{{ task_id }} · scoring: {{ scoring_type }} ·
   task version {{ task_hash }}</div></div>

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

<div class="foot">{{ cost_note|safe }}</div>
<div class="foot">Latest-per-model table ranks by score, then cost, then speed.
Token counts come from provider usage fields. Outputs are verbatim transcripts,
truncated for display — full text lives in runs/…/transcript.jsonl.</div>
{{ sort_js }}
</body></html>"""

INDEX_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM Testing · Overview</title>
{% if dataset_key == "live" %}<link rel="alternate" type="application/atom+xml" title="LLM Testing — models tested" href="feed.xml">{% endif %}
<style>{{ css }}
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
</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>LLM Testing</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><select id="dsnav" title="switch dataset version"
    style="background:var(--surface);color:var(--ink);border:1px solid var(--border);
    border-radius:7px;padding:4px 8px;font:inherit;font-size:12.5px"></select>
  <div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}one
  suite version per dataset · suite v{{ suite_version }}{% if data_asof %} ·
  <strong>data as of {{ data_asof }}</strong>{% if dataset_key == "live" %} · <a href="feed.xml">feed</a>{% endif %}{% endif %}</div></div>
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
  } catch (e) { sel.style.display = 'none'; }
})();
</script>

<div class="mast">
  <div class="eyebrow">{% for e in mast_eyebrow %}<span>{{ e }}</span>{% endfor %}</div>
  <div class="statline">
  {% for s in mast_stats %}<div class="stat"><div class="n{% if s.up %} up{% endif %}{% if s.warn %} warn{% endif %}">{{ s.n }}</div><div class="k">{{ s.k }}</div>{% if s.d %}<div class="d">{{ s.d }}</div>{% endif %}</div>
  {% endfor %}</div>
</div>

{% if matrix %}
<h2>Every model, every task <span class="small muted" style="text-transform:none;letter-spacing:0;font-weight:400">· rows ranked by mean · ± is the 95% band across tasks · <span class="tie" style="color:var(--accent);font-weight:700">≈</span> marks models tied with the leader within noise · hover a cell for the task · <a href="info.html#fail">what the colors mean →</a></span></h2>
<div class="seg" id="mxseg" title="narrow the grid to one end of the suite — rows re-rank by that subset's mean">
  <button type="button" data-mx="all" class="on">All ({{ matrix.n_all }})</button>
  <button type="button" data-mx="hard">◆ Hard ({{ matrix.n_hard }})</button>
  <button type="button" data-mx="frontier" title="only the tasks where even the top cohort struggles — the sharpest discrimination">◆◆ Frontier ({{ matrix.n_frontier }})</button>
  <button type="button" data-mx="easy">Easy ({{ matrix.n_easy }})</button>
</div>
<div class="seg" id="mxcoh" title="local and API/CLI models are different constraint classes — a combined mean is not comparable, so pick the one you can actually run. Rows re-rank and the fleet-average row recomputes for the cohort you choose.">
  <button type="button" data-coh="all" class="on">All ({{ matrix.n_models }})</button>
  <button type="button" data-coh="local">Local ⚡ ({{ matrix.n_local }})</button>
  <button type="button" data-coh="remote">API / CLI ({{ matrix.n_remote }})</button>
</div>
<div class="mx-scroll"><div class="mx">
  <div class="mx-row head">
    <div class="mx-rail"><span class="rk"></span><span class="nm">Model</span><span class="sc">Score</span><span class="gp">Gap</span></div>
    <div class="mx-cells">{% for c in matrix.cats %}<div class="mx-grp" style="grid-template-columns:repeat({{ c.n }},15px);gap:3px"><span class="mx-clabel" title="{{ c.key }}" style="grid-column:1/-1">{{ c.code }} <span class="cn">{{ c.n }}</span></span></div>{% endfor %}</div>
  </div>
  {% for r in matrix.rows %}
  <div class="mx-row{% if r.lead %} lead{% endif %}{% if r.partial %} partial{% endif %}" data-all="{{ r.m_all }}" data-hard="{{ r.m_hard }}" data-frontier="{{ r.m_frontier }}" data-easy="{{ r.m_easy }}" data-nobias="{{ r.m_nobias }}" data-kind="{{ r.kind }}"{% if r.partial %} title="only {{ r.cover }} tasks run — ranked below every fully-tested model, because the mean of a partial row is not comparable to a full one"{% endif %}>
    <div class="mx-rail"><span class="rk">{{ r.rank }}</span><span class="nm">{{ r.model }}{% if r.partial %} <span class="pcov">{{ r.cover }}</span>{% endif %}</span><span class="sc">{{ r.score }}{% if r.ci %}<span class="ci" title="95% confidence band across tasks (±1.96·SE)">{{ r.ci }}</span>{% endif %}</span><span class="gp">{% if r.tied %}<span class="tie" title="within the leader's 95% band — not statistically distinguishable on this task set">≈</span>{% endif %}{{ r.gap }}</span></div>
    <div class="mx-cells">{% for g in r.groups %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}" data-sub="{{ cell.sub }}" data-fr="{{ cell.fr }}"{% if cell.v %} data-v="{{ cell.v }}"{% endif %}{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
  {% endfor %}
  <div class="mx-row foot">
    <div class="mx-rail"><span class="fl">fleet avg / task →</span></div>
    <div class="mx-cells">{% for g in matrix.foot %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}" data-sub="{{ cell.sub }}" data-fr="{{ cell.fr }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div>
  </div>
</div></div>
<script>
(function(){
  var seg=document.getElementById('mxseg'), coh=document.getElementById('mxcoh');
  var mx=document.querySelector('.mx');
  if(!seg||!mx) return;
  var rows=[].slice.call(mx.querySelectorAll('.mx-row:not(.head):not(.foot)'));
  var head=mx.querySelector('.mx-row.head'), foot=mx.querySelector('.mx-row.foot');
  var sub='all', cohort='all';
  function vis(g){ return [].slice.call(g.querySelectorAll('.mx-cell')).filter(function(c){ return c.style.display!=='none'; }).length; }
  function inCohort(r){ return cohort==='all'||r.dataset.kind===cohort; }
  function showCell(c){ return (sub==='all')||(sub==='frontier'?c.dataset.fr==='1':c.dataset.sub===sub); }
  function refoot(live){
    if(!foot) return;
    var cells=[].slice.call(foot.querySelectorAll('.mx-cell'));
    var cols=live.map(function(r){ return [].slice.call(r.querySelectorAll('.mx-cell')); });
    cells.forEach(function(f,i){
      var vals=[];
      cols.forEach(function(cs){
        var c=cs[i]; if(!c) return;
        var v=parseFloat(c.dataset.v||'');
        if(!isNaN(v)) vals.push(v);
      });
      var tid=(f.title||'').split(' · ')[0];
      if(!vals.length){
        f.className='mx-cell na'; f.style.removeProperty('--a');
        f.title=tid+' · no data in this cohort';
        return;
      }
      var mean=vals.reduce(function(a,b){ return a+b; },0)/vals.length;
      f.className='mx-cell pass';
      f.style.setProperty('--a', (0.10+0.90*Math.max(0,Math.min(1,mean))).toFixed(3));
      f.title=tid+' · cohort avg '+mean.toFixed(2)+' ('+vals.length+' model'
        +(vals.length===1?'':'s')+')';
    });
  }
  function apply(){
    rows.forEach(function(r){ r.style.display=inCohort(r)?'':'none'; });
    var live=rows.filter(inCohort);
    rows.concat(foot?[foot]:[]).forEach(function(r){
      [].slice.call(r.querySelectorAll('.mx-cell')).forEach(function(c){
        c.style.display=showCell(c)?'':'none';
      });
      [].slice.call(r.querySelectorAll('.mx-grp')).forEach(function(g){
        g.style.display=vis(g)?'':'none';
      });
    });
    refoot(live);
    if(head&&live.length){
      var src=[].slice.call(live[0].querySelectorAll('.mx-grp'));
      [].slice.call(head.querySelectorAll('.mx-grp')).forEach(function(hg,i){
        var n=src[i]?vis(src[i]):0;
        hg.style.display=n?'':'none';
        hg.style.gridTemplateColumns='repeat('+n+',15px)';
        var cn=hg.querySelector('.cn'); if(cn) cn.textContent=n;
      });
    }
    var scored=live.map(function(r){
      return {r:r, v:parseFloat(r.dataset[sub]),
              p:r.classList.contains('partial')}; });
    scored.sort(function(a,b){
      if(a.p!==b.p) return a.p?1:-1;
      return (isNaN(b.v)?-1:b.v)-(isNaN(a.v)?-1:a.v); });
    var full=scored.filter(function(o){ return !o.p&&!isNaN(o.v); });
    var lead=full.length?full[0].v:NaN, parent=rows.length?rows[0].parentNode:null;
    var rk_n=0;
    rows.forEach(function(r){ r.classList.remove('lead'); });
    scored.forEach(function(o,i){
      if(parent&&foot) parent.insertBefore(o.r,foot);
      var sc=o.r.querySelector('.sc'), rk=o.r.querySelector('.rk'), gp=o.r.querySelector('.gp');
      if(!o.p) rk_n++;
      if(sc) sc.textContent=isNaN(o.v)?'—':o.v.toFixed(3);
      if(rk) rk.textContent=o.p?'—':String(rk_n);
      if(gp) gp.textContent=(o.p||rk_n===1||isNaN(o.v)||isNaN(lead))?'—'
        :'+'+(lead-o.v).toFixed(3).replace(/^0/,'');
      o.r.classList.toggle('lead', !o.p&&rk_n===1&&!isNaN(o.v));
    });
    var fl=foot&&foot.querySelector('.fl');
    if(fl) fl.textContent=(cohort==='all'?'fleet':cohort==='local'?'local':'API/CLI')
      +' avg / task →';
  }
  function wire(box, key, set){
    if(!box) return;
    [].slice.call(box.querySelectorAll('button')).forEach(function(b){
      b.addEventListener('click',function(){
        [].slice.call(box.querySelectorAll('button')).forEach(function(x){ x.classList.toggle('on',x===b); });
        set(b.dataset[key]); apply();
      });
    });
  }
  wire(seg,'mx',function(v){ sub=v; });
  wire(coh,'coh',function(v){ cohort=v; });
  apply();
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
<div class="seg" data-seg="podium">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local ⚡</button>
  <button data-f="remote">API / CLI</button>
</div>
<div class="podium">
{% for p in podium %}
<a class="pcard m{{ loop.index if (loop.index <= 3 and not p.partial) else 0 }}" href="models/{{ p.slug }}.html" data-kind="{{ p.kind }}"{% if p.partial %} data-partial="1"{% endif %}>
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
  <button data-f="frontier">Frontier tasks</button>
  <button data-f="easy">Easy tasks</button>
  <button data-f="nobias" title="ranks on the automated checker alone — the two human-graded tasks are rescaled so a full machine pass is 1.0">No Bias</button>
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
<th data-type="num">Coverage</th>
<th class="num" data-type="num" title="share of requests the endpoint actually answered. Below 100% means the provider refused, throttled, or dropped the connection — the score still carries the loss, this column says whose fault it was">Uptime</th>
<th data-type="num">tok/s</th>
<th data-type="num" title="an estimate, not a bill"><a href="info.html#pricing">Cost/run</a></th>
<th class="num" data-type="num" title="score per dollar; a local model's dollar is measured GPU electricity ⚡">Score / $</th>
<th data-type="num" title="weights on disk + quant; picking a GPU size shows VRAM needed at your context">VRAM / fit</th></tr>
{% for r in standings %}
<tr{% if r.partial %} data-partial="1"{% endif %} data-kind="{{ r.kind }}" data-w="{{ r.w_v }}" data-kvtok="{{ r.kvtok }}"
    data-kvfixed="{{ r.kvfixed }}" data-native="{{ r.native }}"
    data-pure="{{ r.pure_v }}" data-value="{{ r.value_v }}" data-speed="{{ r.speed_v }}"
    data-eff="{{ r.eff_v }}" data-hard="{{ r.hard_v }}" data-frontier="{{ r.frontier_v }}" data-easy="{{ r.easy_v }}" data-nobias="{{ r.nobias_v }}" data-firsttry="{{ r.firsttry_v }}">
<td class="num">{{ r.rank }}</td>
<td class="nowrap">{{ r.model }}</td>
<td class="num lensval" data-sort="{{ r.score_v }}">{{ r.score }}</td>
<td class="small">{{ r.where }}</td>
<td class="num" data-sort="{{ r.score_v }}">{{ r.score }}</td>
<td class="num" data-sort="{{ r.low_v }}" title="worst task: {{ r.low_task }}">{{ r.low }}</td>
<td class="num">{{ r.cov }}</td>
<td class="num{% if r.avail_v != '1.0000' %} warn{% endif %}" data-sort="{{ r.avail_v }}"
    title="{{ r.avail_why }}">{{ r.avail }}</td>
<td class="num" data-sort="{{ r.tps_v }}">{{ r.tps }}</td>
<td class="num">{{ r.cost }}</td>
<td class="num">{{ r.value }}</td>
<td class="small fitcell num" data-size="{{ r.size_disp }}">{{ r.size_disp }}</td></tr>
{% endfor %}</table></div>
<div class="foot" style="margin-top:6px">Local and API/CLI models are different
constraint classes — a combined mean isn't comparable, so filter to yours.
<b>Uptime</b> is the share of requests the endpoint answered at all; a
figure below 100% is the provider throttling, refusing or dropping, not the
model reasoning badly — hover it for which tasks and why.
<b>Score / $</b> is quality per dollar; for a local model that dollar is
<b>measured GPU electricity</b> (⚡), not an API bill. <b>VRAM / fit</b> is the
model's weights on disk; pick a GPU size under <b>Local</b> to see the VRAM it
needs at your context (weights + KV cache) and whether it fits — measured from
the GGUF, not the run's loaded window.</div>
{% endif %}

{% if bump %}
<h2>Rankings across suite versions</h2>
<div class="seg" data-seg="bump">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local ⚡</button>
  <button data-f="remote">API / CLI</button>
</div>
{% for key in ['all','local','remote'] %}
<div data-bcohort="{{ key }}"{% if key != 'all' %} style="display:none"{% endif %}>
{% if bumps[key] %}<div class="card chartcard">{{ bumps[key] }}</div>
{% else %}<p class="muted small">not enough versions with {{ 'local' if key == 'local' else 'API / CLI' }} coverage to trace a rank.</p>{% endif %}
</div>
{% endfor %}
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
<div class="seg" data-seg="valspeed">
  <button class="on" data-f="all">All</button>
  <button data-f="local">Local ⚡</button>
  <button data-f="remote">API / CLI</button>
</div>
{% for key in ['all','local','remote'] %}
<div data-vcohort="{{ key }}"{% if key != 'all' %} style="display:none"{% endif %}>
  {% if cost_scatter[key] %}
  <div class="foot" style="margin:0 0 8px">{{ cost_note|safe }}</div>
  <div class="foot" style="margin:0 0 4px">Score vs <b>cost to run the full
    suite</b> — API / CLI models (a local model's "cost" is just electricity)</div>
  <div class="card chartcard">{{ cost_scatter[key] }}</div>
  {% elif key == 'local' %}
  <div class="foot" style="margin:0 0 4px">No cost chart for local models — what
    they cost is electricity, not API spend, so there is nothing to plot against
    score here. Their speed is below.</div>
  {% endif %}
  <div class="foot" style="margin:14px 0 4px">Score vs <b>generation speed</b></div>
  <div class="card chartcard">{{ speed_scatter[key] }}</div>
</div>
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
<th data-type="text" title="◆ = in the hardened suite = Hard ∪ Frontier (the overview's discriminating tiers), the set chosen for 3× repeat runs — derived live, not hand-curated.">3×</th></tr>
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
{% if not public_nav %}<td><button class="delrun" data-run="{{ r.run_id }}"
  title="delete this run's data permanently">✕</button></td>{% endif %}</tr>
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

(() => {
  const svg = document.querySelector('svg.bump');
  if (!svg) return;
  const groups = [...svg.querySelectorAll('.bm')];
  const light = (slugs) => {
    svg.classList.toggle('focus', !!slugs);
    groups.forEach(g => g.classList.toggle('on',
      !!slugs && slugs.indexOf(g.dataset.m) !== -1));
  };
  svg.querySelectorAll('.bmhit').forEach(h => {
    const ms = h.dataset.ms.split(',');
    h.addEventListener('mouseenter', () => light(ms));
    h.addEventListener('mouseleave', () => light(null));
  });
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
every retry. A ✓ after a cost means it is the gateway's actual billed amount
(OpenRouter usage accounting) rather than yaml list pricing; "via &lt;host&gt;"
names the upstream provider that actually served the requests.{% if not public_nav %}
Chart colors and overview visibility are per-model settings on the
<a href="/run">Run</a> page.{% endif %}</div>
<div class="foot">{{ cost_note|safe }}</div>
<script>
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
  frontier: 'Ranked by score on the FRONTIER subset — only the tasks where even the top cohort struggles. The sharpest cut, but a small set: expect wide confidence bands and near-ties until more frontier tasks are added.',
  easy: 'Ranked by score on the easy subset — the tasks almost every model gets right. The order here is SUPPOSED to be flat: if a model drops on this lens it is failing the everyday work, not the frontier.',
  nobias: 'Ranked with every human judgment removed — the automated checker alone, with the two craft-graded tasks rescaled so a full machine pass counts as 1.0. See <a href="info.html#nobias">No Bias</a>.',
  firsttry: 'Ranked by first-try-clean rate: the share of tasks nailed at 1.0 with zero retries.'
};
const LENS_META = {
  pure:    {label:'Score',       fmt:v=>v.toFixed(3)},
  value:   {label:'Score / $',   fmt:v=>v.toLocaleString(undefined,{maximumFractionDigits:1})},
  speed:   {label:'Score / min', fmt:v=>v.toFixed(2)},
  eff:     {label:'Efficiency',  fmt:v=>v>=10?'frontier':'dominated'},
  hard:    {label:'Hard score',  fmt:v=>v.toFixed(3)},
  frontier:{label:'Frontier score', fmt:v=>v.toFixed(3)},
  easy:    {label:'Easy score',  fmt:v=>v.toFixed(3)},
  nobias:  {label:'No Bias',     fmt:v=>v.toFixed(3)},
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
  rows.forEach(tr => { const cell = tr.querySelector('.lensval'); if (!cell) return;
    const raw = tr.dataset[lens]; const v = parseFloat(raw);
    cell.textContent = (raw === '' || isNaN(v)) ? '—' : meta.fmt(v);
    cell.setAttribute('data-sort', isNaN(v) ? '' : v);
  });
  const isPart = tr => tr.dataset.partial === '1';
  rows.sort((a, b) => {
    const pa = isPart(a), pb = isPart(b);
    if (pa !== pb) return pa ? 1 : -1;
    return val(b) - val(a);
  });
  const parent = rows[0].parentNode;
  rows.forEach(tr => parent.appendChild(tr));
  let shown = 0, rank = 0, prev = null;
  rows.forEach(tr => {
    if (tr.style.display === 'none') return;
    const cell = tr.querySelector('td');
    if (isPart(tr)) {
      cell.textContent = '—';
      cell.title = 'only part of the suite has run — the mean of a partial row '
        + 'is not comparable to a full one, so it is not ranked';
      return;
    }
    shown++;
    const v = parseFloat(tr.dataset[lens]);
    const key = isNaN(v) ? null : v.toFixed(4);
    if (key === null || key !== prev) rank = shown;
    prev = key;
    cell.textContent = rank;
    cell.title = (key !== null && rows.filter(r => r.style.display !== 'none'
      && !isPart(r) && parseFloat(r.dataset[lens]).toFixed(4) === key).length > 1)
      ? 'tied on this lens — the models share this score, so any order between '
        + 'them is arbitrary; separate them on speed or cost' : '';
  });
}
function applyPodium(f) {
  const cards = [].slice.call(document.querySelectorAll('.podium .pcard'));
  let rank = 0;
  cards.forEach(c => {
    const show = (f === 'all') || (c.dataset.kind === f);
    c.style.display = show ? '' : 'none';
    c.classList.remove('m1', 'm2', 'm3', 'm0');
    const rk = c.querySelector('.rank');
    if (!show) return;
    if (c.dataset.partial === '1') {
      c.classList.add('m0');
      if (rk) rk.innerHTML = '<span style="color:var(--warn)">unranked</span>';
      return;
    }
    rank++;
    c.classList.add(rank <= 3 ? 'm' + rank : 'm0');
    if (rk) rk.textContent = (rank === 1 ? '\\u2605 #1' : '#' + rank);
  });
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
    } else if (seg.dataset.seg === 'bump') {
      const f = btn.dataset.f;
      document.querySelectorAll('[data-bcohort]').forEach(el => {
        el.style.display = (el.dataset.bcohort === f) ? '' : 'none';
      });
    } else if (seg.dataset.seg === 'podium') {
      applyPodium(btn.dataset.f);
    }
  });
});
['gpugb', 'gpuctx', 'gpuhide'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', applyStandings);
});
applyStandings();
</script>
{{ scatter_js }}
{{ sort_js }}
</body></html>"""

_env = Environment(loader=BaseLoader(), autoescape=False)
_TPL_CACHE: dict = {}


def _compiled(src: str):
    t = _TPL_CACHE.get(src)
    if t is None:
        t = _TPL_CACHE[src] = _env.from_string(src)
    return t

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
  function box(v){ var c='vc-cell'; if (v!=null){ if (v>=0.38) c+=' flip-d'; if (v>=0.53) c+=' flip-l'; } return '<span class="'+c+'" style="'+shade(v)+'">'+(v==null?'—':v.toFixed(2))+'</span>'; }
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
        var pa = a.dataset.partial === '1', pb = b.dataset.partial === '1';
        if (pa !== pb) return pa ? 1 : -1;
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
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    k = (len(vals) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def _fmt_score(v: float) -> str:
    return f"{v:.3f}"


def _score_cell(v: float | None) -> str:
    if v is None:
        return '<span class="muted">—</span>'
    st = "good" if v >= 0.8 else ("warn" if v >= 0.4 else "crit")
    return (f'<span class="scv {st}">{_heat_swatch(v)}'
            f'<b>{_fmt_score(v)}</b></span>')


def _att_per_pass(rs: list[dict]) -> dict:
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


_REGISTRY_CACHE: dict | None = None


def _registry():
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        from .registry import load_models
        _REGISTRY_CACHE = {m.name: m for m in load_models(include_disabled=True)}
    return _REGISTRY_CACHE


_COST_NOTE: str | None = None
_COST_NOTE_SCOPE: str = ""


def cost_note(up: str = "") -> str:
    global _COST_NOTE, _COST_NOTE_SCOPE
    scope = f"{config.SPECIAL_DIR}|{config.RUNS_DIR}"
    if _COST_NOTE is not None and _COST_NOTE_SCOPE == scope:
        return _COST_NOTE.replace("{up}", up)
    _COST_NOTE_SCOPE = scope
    from . import apicost
    acc = apicost.accuracy()
    s = apicost.overhead_summary()
    t = s["total"]
    if not acc.get("n") or not t.get("cells"):
        _COST_NOTE = (
            "<b>Claude has no cost figure here, on purpose.</b> Every Claude "
            "model is measured through the Claude Code CLI, which runs on a "
            "<b>subscription</b> — there is no per-token price to report, so "
            "any number would be invented. Every other row is what the provider "
            "billed, or list pricing on real token counts. Claude cost lands "
            "here when the full suite has been run through the API, not before. "
            "<a href=\"{up}info.html#costbasis\">The method</a>.")
        return _COST_NOTE.replace("{up}", up)
    _COST_NOTE = (
        "<b>Claude has no cost figure here, on purpose.</b> Every Claude model is "
        "measured through the Claude Code CLI, which runs on a <b>subscription</b> "
        "— there is no per-token price to report, so any number would be invented. "
        "Every other row is what the provider billed, or list pricing on real "
        "token counts. We tried publishing a derived API-equivalent and "
        "<a href=\"{up}info.html#costbasis\">measurement refuted it twice</a>: the CLI "
        "sends its own instructions, reads its own files and carries its own "
        "conversation, so it consumed <b>16× more input per turn</b> than the same "
        "model doing the same task through an API — a different agent, not a "
        "fixed overhead, and nothing you can subtract. Claude cost lands here when "
        "the full suite has been run through the API, not before.")
    return _COST_NOTE.replace("{up}", up)


_EQUIV_MODELS: dict | None = None


def _model_of(rs: list[dict]):
    global _EQUIV_MODELS
    if not rs or not rs[0].get("model"):
        return None
    if _EQUIV_MODELS is None:
        from .registry import load_models
        _EQUIV_MODELS = _registry()
    return _EQUIV_MODELS.get(rs[0]["model"])


def _is_subscription(rs: list[dict]) -> bool:
    mo = _model_of(rs)
    return bool(mo and mo.is_cli)


def _scaffold_total(rs: list[dict]) -> int:
    from . import apicost
    mo = _model_of(rs)
    if mo is None or apicost.cli_overhead_for(mo) is None:
        return 0
    return int(sum((apicost.api_equivalent(r, mo) or {}).get(
        "scaffold_tokens", 0) for r in rs))


ENDPOINT_KINDS = ("connect", "transport", "rate_limit")
MODEL_KINDS = ("runaway", "format", "timeout", "repetition_loop")

ENDPOINT_PHRASES = (
    "resourceexhausted",
    "request limit reached",
    "returned an empty response",
    "internal server error",
    "bad gateway",
    "service unavailable",
    "overloaded",
    "no instances available",
    "upstream connect error",
)

MODEL_PHRASES = (
    "exceeds the available",
    "maximum context length is",
    "error_max_turns",
)


def attempt_blame(attempt: dict) -> str:
    if not attempt.get("error"):
        return "clean"
    kind = attempt.get("error_kind")
    if kind in ENDPOINT_KINDS:
        return "endpoint"
    if kind in MODEL_KINDS:
        return "model"
    text = str(attempt.get("error") or "").lower()
    if any(p in text for p in MODEL_PHRASES):
        return "model"
    if any(p in text for p in ENDPOINT_PHRASES):
        return "endpoint"
    return "model"


def availability(rs: list[dict]) -> dict:
    from collections import Counter
    attempts = [a for r in rs for a in (r.get("attempts") or [])]
    blame = Counter(attempt_blame(a) for a in attempts)
    n = len(attempts)
    bad = blame.get("endpoint", 0)
    kinds = Counter(a.get("error_kind") or "?" for a in attempts
                    if attempt_blame(a) == "endpoint")
    cells = sorted({(r.get("model"), r.get("task")) for r in rs
                    if any(attempt_blame(a) == "endpoint"
                           for a in (r.get("attempts") or []))})
    return {"attempts": n, "endpoint_failures": bad,
            "model_failures": blame.get("model", 0),
            "availability": (None if not n else round((n - bad) / n, 4)),
            "kinds": dict(kinds.most_common()),
            "cells": [t for _, t in cells],
            "n_cells": len(cells)}


def _avail_cell(s: dict) -> tuple[str, str, str]:
    a = s.get("avail") or {}
    pct = s.get("avail_pct")
    if pct is None or not a.get("attempts"):
        return "—", "1.0000", "no attempts recorded"
    if not a.get("endpoint_failures"):
        return "100%", "1.0000", (f"{a['attempts']} attempts, every one "
                                  f"answered by the endpoint")
    kinds = ", ".join(f"{k}x{v}" for k, v in (a.get("kinds") or {}).items())
    cells = ", ".join(sorted(set(a.get("cells") or []))[:6])
    more = "" if a.get("n_cells", 0) <= 6 else f" +{a['n_cells'] - 6} more"
    return (f"{pct:.1f}%", f"{a['availability']:.4f}",
            f"{a['endpoint_failures']} of {a['attempts']} attempts failed at "
            f"the endpoint, not in the model ({kinds}) — affected tasks: "
            f"{cells}{more}. These still cost the model its score: a model you "
            f"cannot get an answer out of is a worse model to buy.")


def _summarize(rs: list[dict]) -> dict:
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
    cost_asrun, cost_basis, scaffold = cost, "as-run", 0
    if _is_subscription(rs):
        cost_basis = "subscription"
        cost = None
        scaffold = _scaffold_total(rs)
    newest = max(rs, key=lambda r: r.get("started") or "") if rs else {}
    cold = newest.get("model_meta", {}).get("cold_start_ms")
    local = newest.get("model_meta", {}).get("local")
    gpu = newest.get("model_meta", {}).get("gpu") or {}
    gq = newest.get("model_meta", {}).get("gateway_quants") or {}

    avail = availability(rs)

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
    score_per_dollar = (score_sum / eff_cost
                        if eff_cost and eff_cost > 0 else None)
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
        "avail": avail,
        "avail_pct": (None if avail["availability"] is None
                      else round(avail["availability"] * 100, 1)),
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
                 else ("—" if cost is None else fmt_cost(cost))),
        "cost_val": eff_cost,
        "api_cost_val": cost,
        "cost_basis": cost_basis,
        "cost_asrun_val": cost_asrun,
        "cost_asrun": fmt_cost(cost_asrun),
        "scaffold_tokens": scaffold,
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
            _html.escape(f"{h} ({gq[h]})" if gq.get(h) and gq[h] != "unknown"
                         else str(h))
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
    if not energy_wh:
        return 0.0
    rate = _power_cfg().get("cost_per_kwh")
    if not rate:
        return 0.0
    return (energy_wh / 1000.0) * float(rate)


def _energy_cost(energy_wh) -> str:
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
    try:
        from .registry import load_models
        return {m.name: m.model for m in load_models(include_disabled=True)}
    except Exception:
        return {}


def _leader_key(summaries: dict):
    def key(m: str):
        s = summaries[m]
        return (-(s["avg_score_val"] if s["avg_score_val"] is not None else -1),
                s["cost_val"] or 0,
                -(s["tps_val"] or 0))
    return key


def _pre_v05_caveat(dataset_key: str) -> str:
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
    if n_runs <= 1:
        return "", ""
    ids = ", ".join(run_ids)
    if n_scored >= n_runs:
        return f"×{n_runs}", f"score = mean of {n_runs} runs: {ids}"
    return (f"×{n_scored}/{n_runs}",
            f"score = mean of {n_scored} scored of {n_runs} runs "
            f"({n_runs - n_scored} unscored, left out): {ids}")


def _aggregate(entries: list[dict]) -> dict:
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
        _scored = [e for e in entries
                   if e["score"].get("status") == "scored"
                   and e["score"].get("score") is not None]
        src = _scored[-1]
        if min(vals) < max(vals):
            src = next(e for e in reversed(_scored)
                       if e["score"]["score"] == min(vals))
        agg["score"] = {**src["score"], "score": statistics.fmean(vals)}
        agg["score_sigma"] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        for k in ("status", "failure_mode", "stop_reason"):
            if k in src:
                agg[k] = src[k]
    for k in _MEAN_FIELDS:
        nums = [e[k] for e in entries if e.get(k) is not None]
        if nums:
            agg[k] = statistics.fmean(nums)
    agg["attempts"] = [a for e in entries for a in e.get("attempts") or []]
    return agg


def task_spend(task_data: dict | None = None, tids=None) -> list[dict]:
    if task_data is None:
        task_data = collect_task_data(load_all_runs())
    live = set(tids) if tids is not None else set(task_data)
    rows = []
    for tid, info in task_data.items():
        if tid not in live:
            continue
        costs, walls, toks = [], [], []
        for e in info["agg"].values():
            if e.get("cost_usd") is not None:
                costs.append(e["cost_usd"])
            if e.get("wall_ms") is not None:
                walls.append(e["wall_ms"])
            t = (e.get("tokens_in") or 0) + (e.get("tokens_out") or 0)
            if t:
                toks.append(t)
        rows.append({
            "task": tid, "n_priced": len(costs),
            "cost": (sum(costs) / len(costs)) if costs else None,
            "wall_ms": (sum(walls) / len(walls)) if walls else None,
            "tokens": (sum(toks) / len(toks)) if toks else None,
        })
    rows.sort(key=lambda r: (r["cost"] is None,
                             r["cost"] if r["cost"] is not None else 0,
                             r["tokens"] or 0, r["task"]))
    return rows


def cheapest_tasks(n: int = 10, task_data: dict | None = None,
                   tids=None) -> list[str]:
    return [r["task"] for r in task_spend(task_data, tids)[:max(1, n)]]


UNSTABLE_SIGMA = 0.125


def repeat_coverage(task_data: dict | None = None,
                    tids=None) -> dict:
    if task_data is None:
        task_data = collect_task_data(load_all_runs())
    live = set(tids) if tids is not None else set(task_data)
    per: dict[str, dict] = {}
    unstable_tasks: set[str] = set()
    wobbled_tasks: set[str] = set()
    for tid, info in task_data.items():
        if tid not in live:
            continue
        for model, e in info["agg"].items():
            slot = per.setdefault(model, {"have": [], "todo": [],
                                          "unstable": []})
            if (e.get("n_scored") or 0) < 1:
                continue
            sig = e.get("score_sigma")
            if (e.get("n_scored") or 0) > 1 and sig is not None:
                slot["have"].append(tid)
                if sig > 0:
                    wobbled_tasks.add(tid)
                if sig >= UNSTABLE_SIGMA:
                    slot["unstable"].append(tid)
                    unstable_tasks.add(tid)
            else:
                slot["todo"].append(tid)
    for slot in per.values():
        for k in ("have", "todo", "unstable"):
            slot[k] = sorted(slot[k])
    return {"models": per, "unstable_tasks": sorted(unstable_tasks),
             "wobbled_tasks": sorted(wobbled_tasks),
             "threshold": UNSTABLE_SIGMA, "n_tasks": len(live)}


def _consistency(model: str, task_data: dict) -> dict:
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
    if _GEN_CACHE is not None:
        for k, v in list(_GEN_CACHE.items()):
            if k[0] == "runs" and v is runs:
                return _gen_cached(("td", k[1]),
                                   lambda: _collect_task_data(runs))
    return _collect_task_data(runs)


def _collect_task_data(runs: list[dict]) -> dict[str, dict]:
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
        return {t.id: t for t in _cached_tasks(tasks_dir or config.TASKS_DIR)}
    except Exception:
        return {}


def _model_prefs() -> tuple[dict, set]:
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


def covered_models(task_data: dict, tids=None) -> set[str]:
    ids = list(task_data if tids is None else tids)
    ids = [t for t in ids if t in task_data]
    if not ids:
        return set()
    seen: dict[str, int] = {}
    for tid in ids:
        for m, e in task_data[tid]["agg"].items():
            if (e["score"].get("status") == "scored"
                    and e["score"].get("score") is not None):
                seen[m] = seen.get(m, 0) + 1
    return {m for m, n in seen.items() if n >= len(ids)}


_LOCAL_CACHE: dict[str, bool] = {}


def model_is_local(name: str) -> bool:
    if not _LOCAL_CACHE:
        try:
            from .registry import load_models
            for mo in load_models(include_disabled=True):
                _LOCAL_CACHE[mo.name] = bool(mo.local)
        except Exception:
            _LOCAL_CACHE["__loaded__"] = False
    return bool(_LOCAL_CACHE.get(name, False))


def version_rankings(versions: list[tuple] | None = None,
                     cohort: str = "all") -> list[dict]:
    versions = versions if versions is not None else load_versions()
    _, hidden = _model_prefs()
    out = []
    for key, task_data, _tdefs in versions:
        full = covered_models(task_data)
        if cohort in ("local", "remote"):
            want_local = cohort == "local"
            full = {m for m in full if model_is_local(m) == want_local}
        scores: dict[str, list[float]] = {}
        skipped: set[str] = set()
        for info in task_data.values():
            for m, e in info["agg"].items():
                if m not in full:
                    if m not in hidden:
                        skipped.add(m)
                    continue
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
        out.append({"key": key, "n_models": len(ranks), "ranks": ranks,
                    "n_partial_excluded": len(skipped)})
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
    from .registry import infer_family, load_models
    reg = _registry()
    names = {mm for _k, td, _t in versions for info in td.values()
             for mm in info["agg"]}
    out = {}
    for n in names:
        m = reg.get(n)
        out[n] = m.family_name if m else infer_family(n, n)
    return out


def bump_chart(versions: list[dict], colors: dict[str, str],
               width=1120) -> str:
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


LENS_LABEL = {"frontier": "◆◆ frontier", "hard": "◆ hard",
              "easy": "easy", "mid": "unclassified"}


def lens_badge(tid: str, dstats: dict | None = None) -> dict | None:
    d = dstats or discrimination_stats(load_all_runs(), _task_defs())
    row = next((r for r in d["rows"] if r["tid"] == tid), None)
    if row is None:
        return None
    flag = row["flag"]
    key = ("frontier" if flag == "frontier"
           else "hard" if flag in HARD_FLAGS
           else "easy" if flag in ("ceiling", "dead") else "mid")
    top = row.get("top_mean")
    gap = row.get("gap")
    why = (f"{LENS_LABEL[key]} — spread {row['sd']:.2f} across "
           f"{row['n']} models, top-{d['cohort_k']} mean "
           f"{'—' if top is None else f'{top:.2f}'}"
           + ("" if gap is None else f", top-to-bottom gap {gap:+.2f}")
           + f". Classified {flag}.")
    return {"key": key, "label": LENS_LABEL[key], "why": why, "flag": flag}


def build_task_report(task_id: str, info: dict, tdef,
                      acfg: dict | None = None, suspect: dict | None = None,
                      dstats: dict | None = None) -> str:
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

    return _compiled(TASK_TEMPLATE).render(
        cost_note=cost_note("../"),
        nav=_nav("../"), brand=_brand("../"),
        sort_js=_SORT_JS, focus_js=_FOCUS_JS,
        files_col=(_RUNS_BASE == config.RUNS_DIR),
        css=BASE_CSS, task_id=task_id,
        title=html.escape(tdef.title) if tdef else task_id,
        category=info["category"], tier=info["tier"],
        lens=lens_badge(task_id, dstats),
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
    return _compiled(RUN_TEMPLATE).render(
        cost_note=cost_note("../"),
        nav=_nav("../"), brand=_brand("../"),
        sort_js=_SORT_JS,
        css=BASE_CSS, run_id=run["run_id"], manifest=run["manifest"],
        env_line=html.escape(env_line), run_rollup=run_rollup,
        tiles=tiles, summaries=summaries, models=models, grid=grid, details=details)


MODEL_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ model }} · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>{{ model }}</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">{{ where }} · {{ dataset_label or "live dataset" }} ·
  aggregated result per task across {{ n_runs }} run(s)
  {% for l in model_links %}<a class="reflink" href="{{ l.url }}" target="_blank"
    rel="noopener">{{ l.short }}</a>{% endfor %}</div></div>

<div class="tiles">
{% for t in tiles %}<div class="tile"><div class="v">{{ t.v }}{% if t.sub %}<span class="vsub" title="{{ t.sub_tip }}">{{ t.sub }}</span>{% endif %}</div><div class="k">{{ t.k }}</div></div>
{% endfor %}</div>

{% if detail_rows %}
<h2>Model details — what we tested</h2>
<div class="card"><table>
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
<div class="card vc-wrap">
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

<div class="foot">{{ cost_note|safe }}</div>
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


def _cli_effort_default() -> str | None:
    from .runner import _cli_effort_default as _d
    try:
        return _d()
    except Exception:
        return None


def _model_detail_rows(mo, mi: dict, fp, hosts: list,
                       summary: dict | None = None) -> list[dict]:
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
        bits = [f"{mo.max_tokens:,} max tokens"]
        if not mo.sampling_settable:
            bits.append("sampling: <b>not settable</b> — "
                        + html.escape(mo.unsettable_reason))
        else:
            if mo.temperature is None:
                bits.append("temperature: <b>not settable</b> (provider default)")
            else:
                bits.append(f"temperature {mo.temperature}")
            for k in mo.SAMPLING_KEYS:
                v = (mo.sampling or {}).get(k)
                if v is not None:
                    bits.append(f"{k} {v}")
        _why = ""
        if mo.local and mo.max_tokens < 65536:
            _why = ("local: the budget also sizes the loaded context window, so a "
                    "larger one would spill VRAM to shared memory")
        elif not mo.local and mo.max_tokens < 65536:
            _why = ("held below the fleet ceiling because this model's provider "
                    "caps completions here")
        unset = ([k for k in mo.SAMPLING_KEYS
                  if (mo.sampling or {}).get(k) is None]
                 if mo.sampling_settable else [])
        if not mo.sampling_settable:
            _note = ("<b>Nothing was transmitted.</b> Every sampling value this "
                     "model ran under is the provider's own, and no number here "
                     "was chosen by us. ")
        elif unset:
            _note = ("Not sent, so left at this provider's own default: <code>"
                     + "</code>, <code>".join(unset) + "</code>. "
                     "Provider defaults are not uniform — llama.cpp behind LM "
                     "Studio applies its own top-k and repeat penalty where a "
                     "gateway typically disables them — so \"unset\" means "
                     "\"whatever this provider does\", not a value we chose. ")
        else:
            _note = "Every sampling parameter was set explicitly. "
        add("Sampling (as tested)", " · ".join(bits)
            + '<div class="note" style="font-size:11.5px;margin-top:2px">'
            + _note
            + (f"<b>Budget note:</b> {_why}." if _why else "") + "</div>")
        if mo.sampling_profiles:
            from . import config as _cfg
            rows_p = []
            for prof, vals in sorted(mo.sampling_profiles.items()):
                cats = sorted(c for c, p in
                              _cfg.CATEGORY_SAMPLING_PROFILE.items() if p == prof)
                shown = " · ".join(f"{k} {v}" for k, v in sorted(vals.items()))
                rows_p.append(f"<b>{html.escape(prof)}</b> → {shown}"
                              + (f'<div class="note" style="font-size:11px">'
                                 f'applies to: {", ".join(cats)}</div>'
                                 if cats else
                                 '<div class="note" style="font-size:11px">'
                                 'no task category maps to this profile</div>'))
            add("Sampling by use case",
                "<div>" + "</div><div style='margin-top:3px'>".join(rows_p) + "</div>"
                + '<div class="note" style="font-size:11.5px;margin-top:3px">'
                "The creator publishes different settings for different kinds of "
                "work, so each task category draws from the profile above that "
                "matches it. A category with no matching profile uses the base "
                "row.</div>")
        if mo.effort_settable:
            lvl = mo.effort_as_tested
            if lvl == "inherited":
                amb = _cli_effort_default()
                shown = (f'<b>not set by the harness</b> — inherited from the '
                         f'CLI session'
                         + (f", currently <code>{html.escape(amb)}</code>"
                            if amb else ""))
                note = ("This transport takes <code>--effort</code> "
                        f"({', '.join(mo.EFFORT_LEVELS)}), and the harness does "
                        "not pass it, so the level is whatever the operator's "
                        "CLI configuration says at the moment of the run. Runs "
                        "recorded before this was tracked do not state their "
                        "level at all, so those scores cannot be pinned to one.")
            else:
                shown = f"<b><code>{html.escape(lvl)}</code></b>"
                note = ("Passed explicitly as <code>--effort</code>, so the run "
                        "does not depend on the operator's CLI configuration.")
            add("Reasoning effort (as tested)", shown
                + '<div class="note" style="font-size:11.5px;margin-top:2px">'
                + note + " <a href=\"../info.html#effort\">How this is "
                "decided</a>.</div>")
        if (summary or {}).get("cost_basis") == "subscription":
            from . import apicost as _ac
            _oh = _ac.cli_overhead_for(mo)
            _sc = int((summary or {}).get("scaffold_tokens") or 0)
            add("Cost",
                "<b>not reported</b> &mdash; subscription"
                '<div class="note" style="font-size:11.5px;margin-top:2px">'
                "Measured through the Claude Code CLI, which runs on a "
                "subscription: there is no per-token price, so any figure here "
                "would be invented. This model is also left out of the value and "
                "cost-per-point views."
                + (f" For scale, the CLI sent <b>{int(_oh):,}</b> input tokens of "
                   f"its own instructions and tools per request "
                   f"({_sc:,} across this model's cells) &mdash; but that is not a "
                   f"deduction you can make, because the CLI is a different agent "
                   f"doing more work, not a wrapper." if _oh else "")
                + " Cost arrives when the full suite has been run through the API. "
                "<a href=\"../info.html#costbasis\">Why, and what we measured</a>."
                "</div>")
        if mo.sampling_source:
            src = html.escape(str(mo.sampling_source))
            add("Sampling reference",
                f'<a href="{src}" rel="nofollow noopener">{src}</a>'
                '<div class="note" style="font-size:11.5px;margin-top:2px">'
                "the creator's published recommendation these values came "
                "from</div>")
        else:
            add("Sampling reference",
                '<span class="note">none recorded — these are the suite\'s '
                "house defaults, not a vendor recommendation</span>")
        if not mo.local:
            p = mo.pricing or {}
            if p.get("input_per_mtok") or p.get("output_per_mtok"):
                add("List price", f"${p.get('input_per_mtok', 0)}/M tok in · "
                    f"${p.get('output_per_mtok', 0)}/M tok out")
    if hosts:
        add("Served by (gateway host)", html.escape(", ".join(hosts)))
    return rows


def _cat_code(tids: list[str]) -> str:
    return tids[0].split("-")[0].upper() if tids else ""


def _mx_cell(entry, tdef, acfg, suspect, href):
    from . import assess as _assess
    tid = tdef.id
    if entry is None:
        return {"cls": "na", "a": "0", "tip": f"{tid} · not run", "href": href}
    cat = _assess.classify(entry, tdef, acfg, suspect)["category"]
    sc = entry.get("score") or {}
    val = sc.get("score")
    counted = (sc.get("status") == "scored" and val is not None)
    v_attr = {"v": f"{val:.6f}"} if counted else {}
    if cat == "fell-for-trap":
        return {"cls": "trap", "a": "0", "tip": f"{tid} · fell-for-trap",
                "href": href, **v_attr}
    if cat == "retrieval-miss":
        return {"cls": "miss", "a": "0", "tip": f"{tid} · retrieval-miss",
                "href": href, **v_attr}
    if cat in ("rumination-spiral", "runaway", "incomplete-output",
               "agentic-max-turns", "infinite-loop"):
        return {"cls": "dnf", "a": "0", "tip": f"{tid} · {cat}", "href": href,
                **v_attr}
    if counted:
        v = max(0.0, min(1.0, val))
        return {"cls": "pass", "a": f"{0.10 + 0.90 * v:.3f}", "v": f"{val:.6f}",
                "tip": f"{tid} · {val:.2f}", "href": href}
    return {"cls": "na", "a": "0", "tip": f"{tid} · {cat}", "href": href}


def _mirror_detail_row(entry: dict | None) -> dict | None:
    if not entry:
        return None
    d = entry["delta"]
    col = {"suspect": "#d03b3b", "watch": "#fab219"}.get(entry.get("band"),
                                                        "#0ca30c")
    pairs = " · ".join(
        f'{html.escape(p["task"])} {p["public"]:.2f}→{p["private"]:.2f}'
        for p in entry.get("pairs") or [])
    return {"k": "Held-out mirror (contamination)",
            "v": (f'public <b>{entry["public"]:.3f}</b> vs private '
                  f'<b>{entry["private"]:.3f}</b> on {entry["n"]} re-seeded '
                  f'task(s) · delta <b style="color:{col}">{d:+.3f}</b> '
                  f'<span style="color:{col}">({entry.get("band", "flat")})</span>'
                  '<div class="note" style="font-size:11.5px;margin-top:2px">'
                  'The same task shapes regenerated at a different seed and never '
                  'published, so a memorized instance cannot help. Positive means '
                  'this model did better on the <em>published</em> instance. One '
                  f'task differing moves this by {entry.get("one_task", 0):.3f}, so '
                  '<b>flat</b> is within one task\'s worth and the expected result '
                  '— re-seeding is not difficulty-neutral. '
                  f'Per task: {pairs}. '
                  '<a href="../info.html#mirror">How this is measured</a>.</div>')}


def _confirmed_row(entry: dict | None) -> dict | None:
    if not entry or not entry.get("total"):
        return None
    ok, bad, none = entry["confirmed"], entry["mismatched"], entry["unlogged"]
    if bad:
        det = "; ".join(f"{html.escape(t)}: {html.escape('; '.join(d))}"
                        for t, d in entry["details"][:4])
        val = (f'<b style="color:#d03b3b">{bad} of {entry["total"]} request(s) '
               f'did NOT match what was sent</b>'
               '<div class="note" style="font-size:11.5px;margin-top:2px">'
               f'{det}</div>')
    else:
        val = (f'<b style="color:#0ca30c">{ok} of {entry["total"]}</b> request(s) '
               'confirmed identical to what was sent'
               + (f' · {none} predate the server log and cannot be checked'
                  if none else ""))
    return {"k": "Sampling confirmed received",
            "v": val + '<div class="note" style="font-size:11.5px;margin-top:2px">'
            "Read back from LM Studio's own request log, not from our side: the "
            "values this model was <em>configured</em> with are one claim, the "
            "values the server <em>received</em> are another. Only local models "
            "can be checked this way — a gateway keeps no log we can read.</div>"}


def _lens_row(model: str, dstats: dict | None = None) -> dict | None:
    d = dstats
    if d is None:
        return None
    subs = (("frontier", d.get("frontier_subset") or [], "#d03b3b"),
            ("hard", d.get("hard_subset") or [], "#fab219"),
            ("easy", d.get("easy_subset") or [], "#0ca30c"))
    td = {tid: r for tid, r in
          ((row["tid"], row) for row in d.get("rows") or [])}
    cells = d.get("per_model_scores") or {}
    parts, missing = [], []
    for name, ids, col in subs:
        vals = [cells[(model, tid)] for tid in ids
                if (model, tid) in cells]
        if not vals:
            missing.append(name)
            continue
        mean = sum(vals) / len(vals)
        parts.append(f'<b style="color:{col}">{name} {mean:.3f}</b>'
                     f'<span class="note" style="font-size:11px"> '
                     f'({len(vals)}/{len(ids)})</span>')
    if not parts:
        return None
    return {"k": "Score by difficulty lens",
            "v": (" · ".join(parts)
                  + '<div class="note" style="font-size:11.5px;margin-top:2px">'
                    'The same runs, split by how much each task separates the '
                    'fleet. A single mean hides where a model actually loses: '
                    'easy tasks are the ones nearly everything passes, hard '
                    'ones split the fleet, frontier ones the top cohort still '
                    'fails. '
                    '<a href="../discriminate.html">How each task is '
                    'classified</a>.'
                  + (f' No data yet on: {", ".join(missing)}.' if missing
                     else "")
                  + '</div>')}


def _availability_row(s: dict) -> dict | None:
    a = s.get("avail") or {}
    if not a.get("attempts"):
        return None
    pct = s.get("avail_pct")
    if not a.get("endpoint_failures"):
        return {"k": "Endpoint availability",
                "v": (f'<b>100%</b> — all {a["attempts"]} requests answered'
                      '<div class="note" style="font-size:11.5px;margin-top:2px">'
                      'Every request reached the provider and came back. No score '
                      'here is a plumbing artefact.</div>')}
    col = "#d03b3b" if pct < 95 else "#fab219"
    kinds = " · ".join(f'{html.escape(k)} ×{v}'
                       for k, v in (a.get("kinds") or {}).items())
    cells = ", ".join(html.escape(t)
                      for t in sorted(set(a.get("cells") or []))[:8])
    more = "" if a.get("n_cells", 0) <= 8 else f" +{a['n_cells'] - 8} more"
    return {"k": "Endpoint availability",
            "v": (f'<b style="color:{col}">{pct:.1f}%</b> — '
                  f'{a["endpoint_failures"]} of {a["attempts"]} requests failed '
                  f'at the endpoint ({kinds})'
                  '<div class="note" style="font-size:11.5px;margin-top:2px">'
                  'These failed <em>before</em> the model could answer: the '
                  'provider throttled, refused for capacity, returned an empty '
                  'body, or dropped the connection. They still cost this model '
                  'its score, because a model you cannot get an answer out of is '
                  'a worse model to buy — this row says whose fault it was. '
                  f'Affected: {cells}{more}. '
                  '<a href="../info.html#availability">How this is counted</a>.'
                  '</div>')}


def build_model_report(model: str, runs: list[dict], tdefs: dict,
                       dataset_label: str = "",
                       versions: list[tuple] | None = None,
                       mirror_row: dict | None = None,
                       confirmed_row: dict | None = None,
                       dstats: dict | None = None) -> str:
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
                     "detail": _html.escape(str(f.get("detail") or "")),
                     "summary": _html.escape(str(f.get("summary") or "")),
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
    detail_rows = _model_detail_rows(mo, meta_info, fp, hosts, s)
    _lens = _lens_row(model, dstats)
    if _lens:
        detail_rows.append(_lens)
    _av = _availability_row(s)
    if _av:
        detail_rows.append(_av)
    if confirmed_row:
        detail_rows.append(confirmed_row)
    if mirror_row:
        detail_rows.append(mirror_row)
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
    return _compiled(MODEL_TEMPLATE).render(
        cost_note=cost_note("../"),
        nav=_nav("../"), brand=_brand("../"),
        sort_js=_SORT_JS, verscmp=verscmp, verscmp_js=_VERSCMP_JS,
        css=BASE_CSS, model=html.escape(model), slug_q=quote(model),
        where=where, dataset_label=dataset_label, n_runs=len(my_runs),
        tiles=tiles, cats=cats, task_rows=task_rows, run_rows=run_rows,
        runmatrix=runmatrix,
        detail_rows=detail_rows, model_links=model_links, asmt=asmt)


def machine_only_score(entry: dict, tdef) -> float | None:
    cap = float((getattr(tdef, "scoring", None) or {}).get("automated_max", 1.0))
    s = entry.get("score") or {}
    if s.get("status") != "scored":
        return None
    raw = s.get("machine_score")
    if raw is None:
        raw = s.get("score")
    if raw is None:
        return None
    if cap <= 0:
        return None
    return min(1.0, raw / cap)


def machine_only_means(task_data: dict, tdefs: dict) -> dict[str, float]:
    per: dict[str, list[float]] = {}
    for tid, info in task_data.items():
        tdef = tdefs.get(tid)
        if tdef is None:
            continue
        for model, entry in info["agg"].items():
            v = machine_only_score(entry, tdef)
            if v is not None:
                per.setdefault(model, []).append(v)
    return {m: sum(v) / len(v) for m, v in per.items() if v}


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
    _reg = _registry()
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
    bumps = {"all": bump}
    for _c in ("local", "remote"):
        _vr = version_rankings(versions, cohort=_c) if versions else []
        bumps[_c] = bump_chart(_vr, slot) if len(_vr) >= 2 else ""

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

    _cat_task_n = {c: sum(1 for t in tdefs.values() if t.category == c)
                   for c in all_cats}

    def _fit_rows_for(subset: list[str]):
        fr = task_fit({m: by_model.get(m, []) for m in subset}, all_cats,
                      _cat_task_n)
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

            def _tied_disclosure(names):
                inner = "".join(f"<span>{_mlink(m)}{_tag(m)}</span>"
                                for m in sorted(names, key=str.lower))
                return (f"<details class='tiepop'><summary title='every model "
                        f"tied at this score — no order between them is real'>"
                        f"{len(names)} tied</summary>"
                        f"<div class='tp-list'>{inner}</div></details>")

            rows.append({
                "category": row["category"],
                "n_ok": len(ok), "n_total": len(cls),
                "best": (f"{_mlink(tied[0])} <span class='muted'>{best_v:.2f}</span>"
                         + (" " + _tied_disclosure(tied)
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
    _n_full = len(tdefs) or 1
    _full_cov = [m for m in all_models
                 if len(by_model.get(m, [])) >= _n_full]
    for m in _full_cov:
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
            "kind": "local" if s["local"] else "remote",
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

    def _standing(m, rank, cov, partial=False):
        s = summaries[m]
        fp = _footprint(m)
        return {
            "rank": rank, "partial": partial,
            "kind": "local" if s["local"] else "remote",
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
            "avail": _avail_cell(s)[0], "avail_v": _avail_cell(s)[1],
            "avail_why": _avail_cell(s)[2],
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
            "frontier_v": (f"{frontier_mean[m]:.4f}" if m in frontier_mean else ""),
            "easy_v": (f"{easy_mean[m]:.4f}" if m in easy_mean else ""),
            "nobias_v": (f"{nobias_mean[m]:.4f}" if m in nobias_mean else ""),
        }

    _dstats = discrimination_stats(runs, tdefs)
    _hardened_set = hardened_from_stats(_dstats)
    nobias_mean = machine_only_means(task_data, tdefs)
    hard_mean = {h["model"]: h["mean"] for h in _dstats["hard_rank"]}
    easy_mean = {h["model"]: h["mean"] for h in _dstats["easy_rank"]}
    frontier_mean = {h["model"]: h["mean"] for h in _dstats["frontier_rank"]}
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
                            f"{len(by_model.get(m, []))}/{n_suite} partial",
                            partial=True)
                  for m in incomplete]

    points = []
    for m in complete:
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
    _plotted = {p["label"] for p in points}
    legend_html = chart_legend([e for e in legend if e["model"] in _plotted])

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
    _cost_chart = pareto_scatter(
        cost_pts, "cost to run the full suite (USD) — cheaper is left; "
        "dashed = best score per dollar", x_minimize=True, x_fmt="${:,.0f}")
    cost_scatter = {"all": _cost_chart, "remote": _cost_chart, "local": ""}
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
            "hardened": tid in _hardened_set,
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

    _n_suite = len(tdefs) or 1
    _cover = {m: len(by_model.get(m, [])) for m in all_models}
    _mrank = sorted(all_models, key=lambda m: (
        _cover[m] < _n_suite,
        -_cover[m] if _cover[m] < _n_suite else 0,
        -(summaries[m]["avg_score_val"]
          if summaries[m]["avg_score_val"] is not None else -1.0), m))
    _full = [m for m in _mrank if _cover[m] >= _n_suite]
    _lead_v = next((summaries[m]["avg_score_val"] for m in _full
                    if summaries[m]["avg_score_val"] is not None), None)
    _lead_m = next((m for m in _full
                    if summaries[m]["avg_score_val"] is not None), None)
    _lead_ci = summaries[_lead_m]["score_ci95"] if _lead_m else None
    _flag_of = {r["tid"]: r["flag"] for r in _dstats["rows"]}
    _sub_of = {tid: ("hard" if _flag_of.get(tid) in HARD_FLAGS
                     else "easy" if _flag_of.get(tid) in ("ceiling", "dead")
                     else "mid") for tid in task_data}
    _hard_ids = [t for t, s in _sub_of.items() if s == "hard"]
    _easy_ids = [t for t, s in _sub_of.items() if s == "easy"]
    _fr_of = {tid: (_flag_of.get(tid) == "frontier") for tid in task_data}
    _frontier_ids = [t for t, v in _fr_of.items() if v]

    def _sub_mean(model, ids):
        xs = [e["score"]["score"] for tid in ids
              if (e := task_data[tid]["agg"].get(model))
              and e["score"].get("status") == "scored"
              and e["score"].get("score") is not None]
        return sum(xs) / len(xs) if xs else None

    matrix_rows = []
    _rk = 0
    for i, m in enumerate(_mrank):
        _partial = _cover[m] < _n_suite
        if not _partial:
            _rk += 1
        agg = summaries[m]["avg_score_val"]
        groups = [[{**_mcell(task_data[tid]["agg"].get(m), tdefs[tid], m),
                    "sub": _sub_of[tid], "fr": "1" if _fr_of[tid] else ""}
                   for tid in _cat_tids[c]] for c in _live_cats]
        ci = summaries[m]["score_ci95"]
        if agg is None:
            score_s, gap_s, ci_s, tied = "—", "", "", False
        elif _partial:
            score_s = f"{agg:.3f}"
            ci_s = "" if ci is None else "±" + f"{ci:.3f}".lstrip("0")
            gap_s, tied = "—", False
        else:
            score_s = f"{agg:.3f}"
            gap_s = ("—" if (_rk == 1 or _lead_v is None
                             or abs(agg - _lead_v) < 1e-9)
                     else "+" + f"{_lead_v - agg:.3f}".lstrip("0"))
            ci_s = "" if ci is None else "±" + f"{ci:.3f}".lstrip("0")
            tied = (_rk != 1 and _lead_v is not None and ci is not None
                    and _lead_ci is not None
                    and (agg + ci) >= (_lead_v - _lead_ci))
        _mh, _me = _sub_mean(m, _hard_ids), _sub_mean(m, _easy_ids)
        _mf = _sub_mean(m, _frontier_ids)
        _mn = nobias_mean.get(m)
        matrix_rows.append({
            "rank": ("—" if _partial else _rk), "model": _mlink(m),
            "score": score_s,
            "ci": ci_s, "tied": tied,
            "gap": gap_s, "lead": (not _partial and _rk == 1 and agg is not None),
            "partial": _partial,
            "cover": f"{_cover[m]}/{_n_suite}",
            "m_all": ("" if agg is None else f"{agg:.6f}"),
            "m_hard": ("" if _mh is None else f"{_mh:.6f}"),
            "m_easy": ("" if _me is None else f"{_me:.6f}"),
            "m_frontier": ("" if _mf is None else f"{_mf:.6f}"),
            "m_nobias": ("" if _mn is None else f"{_mn:.6f}"),
            "kind": "local" if summaries[m]["local"] else "remote",
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
                            "fr": "1" if _fr_of[tid] else "",
                            "a": f"{0.10 + 0.90 * max(0.0, min(1.0, v)):.3f}",
                            "tip": f"{tid} · fleet avg {v:.2f}",
                            "href": f"tasks/{tid}.html"})
            else:
                grp.append({"cls": "na", "a": "0", "sub": _sub_of[tid],
                            "fr": "1" if _fr_of[tid] else "",
                            "tip": f"{tid} · no data",
                            "href": f"tasks/{tid}.html"})
        matrix_foot.append(grp)

    matrix = ({"cats": [{"key": c, "code": _cat_code(_cat_tids[c]), "n": len(_cat_tids[c])} for c in _live_cats],
               "rows": matrix_rows, "foot": matrix_foot,
               "n_hard": len(_hard_ids), "n_easy": len(_easy_ids),
               "n_frontier": len(_frontier_ids), "n_all": len(task_data),
               "n_models": len(matrix_rows),
               "n_local": sum(1 for r in matrix_rows
                              if r["kind"] == "local"),
               "n_remote": sum(1 for r in matrix_rows
                               if r["kind"] == "remote")}
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

    return _compiled(INDEX_TEMPLATE).render(
        cost_note=cost_note(),
        nav=_nav(""), brand=_brand(""), public_nav=_PUBLIC_NAV,
        sort_js=_SORT_JS,
        css=BASE_CSS, tiles=tiles, runs=runs_view, run_ids=run_ids,
        mast_eyebrow=mast_eyebrow, mast_stats=mast_stats, matrix=matrix,
        podium=podium, standings=standings, task_rows=task_rows,
        frontier=frontier, bump=bump, bumps=bumps,
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
        "changed. Those punish a memorized answer and reward actually reading.",
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
    ("A model that reasons past its output budget scores 0, and that is a choice.",
     "Some models think in a separate channel that is billed as output. One can "
     "spend its <em>entire</em> allowance reasoning and emit almost nothing a "
     "checker can read — measured here at <strong>32,766 of 32,768 tokens "
     "reasoning and two tokens of answer, eleven attempts out of eighteen</strong>. "
     "We score that <strong>0</strong>, the same as a wrong answer, and it is "
     "worth being plain that this is a decision rather than an oversight: the "
     "budget is uniform, and a model that cannot fit its reasoning inside it did "
     "not complete the task under the conditions everyone else faced. The cost of "
     "the choice is real, though — that 0 does not distinguish "
     "<em>could not do it</em> from <em>was not given room to say so</em>, and the "
     "same model may well answer correctly at a larger budget. Where a cell hit "
     "its ceiling having emitted essentially nothing, the "
     "<a href=\"special.html\">Special</a> page can re-run it with the budget "
     "raised; those probe results are experimental and counted toward nothing, "
     "existing purely so the question is answerable rather than assumed."),
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
     "orders of magnitude slower than the optimized one. But an absolute "
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
    ("Colors and dots",
     "Every chart on the overview shares <strong>one color per model</strong>, "
     "so a model is the same color everywhere. Charts are dots rather than "
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
<div class="topbar">{{ brand }}<div class="ttl"><h1>LLM Testing</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">what the tests do · what the numbers mean · changelog</div></div>
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

<h2 id="effort">Reasoning effort — the setting we were not controlling</h2>
<p>Claude models here run through the <code>claude</code> CLI, which exposes a
<strong>reasoning effort</strong> control — <code>--effort</code>, taking
<code>low</code>, <code>medium</code>, <code>high</code>, <code>xhigh</code> or
<code>max</code>. It changes how long the model thinks before answering, and on a
benchmark that is not a cosmetic setting.</p>
<p><strong>The harness was not passing it.</strong> The CLI therefore fell back to
whatever the operator's own configuration said —
<code>effortLevel</code> in a <code>settings.json</code> that lives outside this
repository, is not versioned with it, and was not recorded in any run. So for the
Claude models: <strong>the effort level that produced their scores is not
reconstructible from the data</strong>, and if that file changed between runs, two
Claude numbers on this site are not strictly comparable. That is stated here rather
than left for someone to find.</p>
<p>What changed: every run now <strong>records</strong> the level it used, per cell
and in its manifest, and a level set in a model's yaml is passed explicitly so the
run no longer depends on ambient configuration. Each Claude model's page carries a
<em>Reasoning effort (as tested)</em> row reading either the explicit level or
<em>inherited</em>, and <em>inherited</em> means exactly what it says.</p>
<p><strong>How the level gets chosen.</strong> The same rule as every other knob on
this site: only what a provider documents, and only what the transport can actually
deliver. No other model in the fleet exposes an equivalent — an OpenAI reasoning
model takes no such parameter through the gateway, and a local model has no notion
of it — so effort is a <em>Claude-only</em> dimension and cannot be equalized across
the board. Raising it for Claude and leaving everyone else at their default would
buy Claude thinking time the others were never offered, which is why the level is
disclosed per model instead of tuned for a better number.</p>
<p class="small muted">One limit worth stating: that the flag exists and is accepted
is verified from the CLI's own help. Whether it measurably changes output in
non-interactive <code>-p</code> mode has not yet been tested here, so no level is
set in any model's yaml until it has been — declaring a value that turns out to be
ignored would be the same fiction as a temperature a provider silently drops.</p>

<h3 id="nobias">The "No Bias" lens — the same data with every human judgment removed</h3>
<p>A craft score is set by a person, which makes it the one number on this site
that another person could reasonably disagree with. So the overview carries a
<strong>No Bias</strong> option in its <em>Ranked by</em> control that takes the
human out entirely and ranks on <strong>what the automated checker measured, and
nothing else</strong>.</p>
<p>It does not drop the two tasks — dropping them would quietly shrink the suite
and change what is being compared. Instead each one is <strong>rescaled to its own
machine ceiling</strong>: a submission that passed every mechanical check scores
{{ human_graded[0].cap }} today and counts as <strong>1.000</strong> under this
lens, and one that passed half its checks counts as 0.500. Every other task is
already fully automatic, so its number does not move at all.</p>
<p>Two things to hold onto when reading it. This lens is <strong>not the headline
number and is not more correct</strong> — craft is a real part of what a render
task measures, and a coin with mirrored lettering passes every mechanical check
there is, which is the whole reason a person looks at it. And it is not a claim
that the reviewer got anything wrong: the machine's own number is kept beside
every human score precisely so this view can be computed at all. It answers one
narrow question — <em>how would the board look if only the checker had a vote?</em>
— and leaves the published ranking alone.</p>
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
<li><strong>Output budget, and why it is not identical for everyone.</strong> The
budget is a <em>runaway backstop</em>, not a fairness device — the model is never
told the number, so it cannot plan around it, and truncating mid-sentence would
measure verbosity rather than skill. It is sized well clear of real use (the 99th
percentile of actual output is ~27k tokens). Cloud models get 65,536; local
models get 32,768, because a local model's budget also sizes its loaded context
window and a bigger one spills VRAM to shared memory — a hardware limit, not a
policy choice. One model (<code>laguna-xs-2.1</code>) is held lower still because
its provider caps completions there. The Claude CLI accepts no budget flag, so
the cap is applied after the fact: output past it is discarded exactly as a
provider would have refused to generate it.</li>
<li><strong>Every knob we set, in one place.</strong> These are the suite-wide
configuration choices, not per-model ones. Each is a decision that could have
gone another way, so it is listed rather than left to be discovered:
<ul>
<li><b>Output budget</b> — cloud 65,536 tokens, local 32,768, and any model whose
provider caps completions lower is held at its provider's limit. A
<em>backstop</em>, not a fairness lever: the model is never told the number.</li>
<li><b>Temperature</b> — 0.2 where we can set it, and there are three ways we
cannot. Moonshot fixes kimi-k3 at 1.0 server-side (it <em>refuses</em> anything
else). The Claude CLI exposes no flag at all. And the OpenAI reasoning models take
no sampling parameters whatsoever — behind a gateway an unsupported one is
<em>dropped rather than refused</em>, so it would silently never apply. Each of
those is marked <b>not settable</b> on the model's own page, with the reason,
instead of showing a number that never reached the model.</li>
<li><b>Reasoning effort</b> — the Claude CLI takes <code>--effort</code>
(low / medium / high / xhigh / max), and it is the one setting on this site that
was <strong>never ours to begin with</strong>. See <a href="#effort">Reasoning
effort</a> below: the harness has not been passing it, so every Claude score was
produced at whatever the operator's CLI was configured to, and older runs do not
record which. No other provider in the fleet exposes an equivalent control.</li>
<li><b>Other sampling</b> (top_p, top_k, min_p, penalties, seed) — <em>not sent
at all</em> unless a model's page lists it. An unsent knob runs at the provider's
own default; we do not substitute a house value silently.</li>
<li><b>Retries</b> — one retry per task. A retry is kept because across this
dataset it rescued 7 of 8 timed-out cells, usually a cold model load or a slow
first token. It does mean a model that fails transiently gets a second attempt
while one that succeeds immediately does not — unequal trials, stated plainly.</li>
<li><b>A refused request is not a score.</b> A provider 4xx (bad parameter,
unknown model, bad key) means the model never saw the prompt, so the task is
dropped unscored and that model stops for the run — the same refusal would repeat
on every remaining task. A context-overflow 400 is deliberately excluded: that is
a real limit and still scores zero.</li>
<li><b>Cache pricing</b> — a cache discount is only applied where the provider
publishes one. Anthropic's 0.10×/1.25× is applied to Anthropic; everyone else
prices cached input at the full rate until a real number is configured, so we
never flatter a model's cost with an invented discount.</li>
<li><b>Timing and local cost are machine-specific.</b> The timing-scored task and
every local $/run figure were measured on one particular GPU and CPU. They are
not reproducible on different hardware and should not be read as portable.</li>
</ul></li>
<li><strong>Odd per-model configuration is on the model's own page.</strong>
Anything unusual about how a single model was run — a provider-fixed temperature,
a budget held below the fleet ceiling, a sampling value taken from a vendor
recommendation, or the absence of one — appears in the <em>Sampling (as
tested)</em> row of that model's page, with the reason. If a number looks
surprising, that row is where the explanation lives.</li>
<li><strong>Sampling is per model, and stated per model.</strong> There is no
single temperature for the fleet, because some models and transports do not let us
choose one: Moonshot fixes <code>temperature=1.0</code> server-side for kimi-k3,
the Claude CLI exposes no temperature at all, and the OpenAI reasoning models
accept no sampling parameters — so those run at their creator's setting whatever
we write down. The last case is the quiet one: a gateway <em>drops</em> a
parameter the model does not support instead of returning an error, so nothing
fails and the only symptom would be a number on this site that never applied. Such
models are marked <b>not settable</b> and transmit nothing at all. Rather than
pretend otherwise, <strong>every
model's page lists the exact sampling parameters it was run with</strong> — and
the reference URL for the creator recommendation they came from, or an explicit
note that none was recorded and the value is a house default. Only parameters
listed there were transmitted; every other knob ran at the provider's default.
Open any model page and read the <em>Sampling (as tested)</em> row.</li>
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
<li><strong>Behavior over recall.</strong> The one-shot-app and agentic tasks
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

{% if mirror %}
<h3 id="mirror">Measured, not assumed: the private held-out mirror</h3>
<p>Everything above is a design argument. This is a measurement. Publishing the
suite publishes the answers — a correct model reply recorded in
<code>runs/</code> <em>is</em> the answer key, so withholding the tasks would only
cost the auditability that makes the public data worth anything. So instead the
public set stays fully open, and a <strong>private variant of the same task</strong>
is held back: identical shape, identical checker, <strong>regenerated at a
different seed</strong>, never published. A model that scores markedly higher on
the published instance than on the unpublished one has memorized
<em>that instance</em>.</p>
<p><strong>Coverage, stated honestly:</strong> {{ mirror.n_mirrorable }} of
{{ mirror.n_public }} tasks can be re-seeded and {{ mirror.n_built }} have a
variant built. The rest are hand-written app specs, agent workspaces or fixed
prompts with no generator behind them — they cannot be re-rolled, so
<strong>this check says nothing about them</strong>. It covers the long-context
and reasoning tasks, which is where a memorized payload would pay off most.</p>
{% if mirror.delta %}
<div class="card" style="margin:12px 0">
<table><thead><tr><th data-type="text">Model</th><th class="num">tasks</th>
<th class="num">public</th><th class="num">private (held out)</th>
<th class="num">delta</th><th class="num">verdict</th></tr></thead><tbody>
{% for r in mirror.delta %}
<tr><td class="model">{{ r.model }}</td><td class="num">{{ r.n }}</td>
<td class="num">{{ "%.3f"|format(r.public) }}</td>
<td class="num">{{ "%.3f"|format(r.private) }}</td>
<td class="num"><b style="color:{{ '#d03b3b' if r.band == 'suspect' else
  '#fab219' if r.band == 'watch' else '#0ca30c' }}">{{ "%+.3f"|format(r.delta) }}</b></td>
<td class="num" style="color:{{ '#d03b3b' if r.band == 'suspect' else
  '#fab219' if r.band == 'watch' else '#0ca30c' }}">{{ r.band }}</td></tr>
{% endfor %}
</tbody></table></div>
<p class="small">Positive = better on the published instance. The verdict is sized
against the number of paired tasks rather than a fixed cutoff, because one task
differing moves the mean by <code>1/n</code> — on {{ mirror.n_built }} tasks that
is {{ "%.3f"|format(1.0 / mirror.n_built) if mirror.n_built else "—" }}. So
<b>flat</b> means "within one task's worth", which is the <em>expected</em> result:
re-seeding changes the specific numbers and is not difficulty-neutral, so a small
delta is instance noise rather than evidence. <b>watch</b> is within two tasks'
worth; <b>suspect</b> is beyond that and means read the transcripts, not that a
verdict has been reached. Both score columns use the same aggregation rule as the
rest of the site (every scored run of that model·task, meaned), and each model's
own page shows the per-task pairs.</p>
{% else %}
<p class="small"><strong>No held-out results yet.</strong> The variants are built
and verified different from their public counterparts, but no model has been run
against them, so <strong>no contamination claim is made in either direction</strong>
— this section will fill in with real numbers rather than a reassurance.</p>
{% endif %}
<p class="small">What this catches and what it doesn't: it detects memorization of
the published <em>instance</em>. A model that genuinely learned the skill from the
published task scores the same on both — and should. That is learning, not
cheating, and the delta is designed to read it as such.</p>
{% endif %}

<h2 id="availability">Uptime: whose fault was the zero?</h2>
<p>A score of 0 can mean two very different things, and until now the site
showed them the same way. Either the model answered and got it wrong, or the
<em>endpoint</em> never gave it the chance — throttled, refused for capacity,
returned an empty body, dropped the connection mid-stream.</p>
<p><strong>Both still cost the model its score.</strong> A model you cannot get
an answer out of is a worse model to buy, and the leaderboard is about buying
one. We do not forgive a provider for being oversubscribed. But we do now say
which it was, because "this model is bad" and "this model is fine and its API
is not" are different findings and only one of them is about the model.</p>
<p>Every request the harness makes is recorded as an attempt with an error kind.
<b>Uptime</b> is the share of attempts the endpoint answered at all:</p>
<ul>
<li><b>Charged to the endpoint</b> — <code>rate_limit</code> (HTTP 429),
<code>connect</code> (DNS, reset, connection dropped),
<code>transport</code> (an empty body with no content, tokens or stop reason),
and provider-side refusals identified by their own wording: capacity
exhaustion, 5xx, "no instances available".</li>
<li><b>Charged to the model</b> — <code>runaway</code> (spent the output
budget), <code>format</code> (answered outside the required shape),
<code>timeout</code> (did not finish inside its budget),
<code>repetition_loop</code>, and a rejection for exceeding the model's own
context window. The provider did its job; the model did not.</li>
</ul>
<p>The wording list is best-effort, like every string-matching rule here: a
provider inventing a new phrasing degrades to "charged to the model", which is
the conservative direction — it never invents an excuse for a model.</p>
<p>The one exception, and the only case a cell is dropped rather than scored:
if <em>every</em> attempt failed with <code>connect</code> and no tokens moved
in either direction, no request was ever delivered, so nothing about the model
was measured. That cell gets no score and re-runs. It is a narrow rule on
purpose — a full endpoint still answered, so it still counts.</p>
<p>Each model page carries its own <b>Endpoint availability</b> row naming the
affected tasks. Hover a leaderboard Uptime figure for the same detail.</p>

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

<h3 id="costbasis">Why Claude has no cost figure</h3>
<p>Every Claude model here is measured through the <strong>Claude Code CLI</strong>,
which authenticates against a <strong>subscription</strong>. A subscription has no
per-token price. So there is nothing to report, and the cost column shows
<code>&mdash;</code> rather than a number we invented. Claude is left out of the
value and cost-per-point views for the same reason: you cannot rank a flat fee
against a metered one.</p>
<p>We did try to derive one, and the measurement refuted it &mdash; twice, in
opposite directions. Worth stating plainly, because it is the more interesting
result:</p>
<ul>
<li><strong>First attempt.</strong> The CLI adds its own system prompt and tools to
every request. We measured that at 16,399&ndash;23,740 input tokens per request,
tight to a few tokens across ten tasks, so it looked like a fixed wrapper.
Subtracting it and repricing at API rates suggested the fleet cost barely
moved.</li>
<li><strong>Then we ran the big tasks.</strong> The API came in <strong>1.46&times;
cheaper</strong>, not dearer. The estimate was wrong by a third overall, and wrong
in both directions per task (&minus;70% to +194%).</li>
<li><strong>Why.</strong> It is not a wrapper. On one agentic task the CLI sent
<strong>565,830</strong> input tokens across 14 turns where the same model through
an API sent <strong>30,239</strong> across 12 &mdash; <strong>16&times; more per
turn</strong>. Claude Code brings its own instructions, reads its own files and
carries its own conversation. It is a <em>different agent doing more work</em>, and
both reached 1.00. There is no quantity you can subtract to turn one into the
other.</li>
<li><strong>It moves scores, not just price.</strong> On one render task the same
model and prompt scored <strong>0.18</strong> through the CLI, <strong>0.25</strong>
through the API and <strong>0.00</strong> through a gateway. So a Claude score here
is &ldquo;Claude plus Claude Code&rsquo;s agent&rdquo;, while every other
model&rsquo;s score is &ldquo;the model plus this harness&rsquo;s tool
loop&rdquo;.</li>
</ul>
<p><strong>What happens next.</strong> Claude gets a real cost the only way it can:
by running the full suite through the API, as its own entry, in the same harness
loop as every other model. Until a model has completed the whole suite that way it
is treated like any other partial run and stays out of every ranking. The
CLI-measured entries are kept, because comparing the two agents on identical tasks
is a measurement in its own right.</p>
<p>The avenue comparison behind all of this lives in <code>special/</code> and
counts toward no score.</p>

<h3>Local models are not free — they just bill you differently</h3>
<p>No money goes to a provider, so a local model's <code>$</code> column is ~0.
The wall socket still charges you. The harness samples the GPU throughout every
local run, so this is <strong>measured, not modeled</strong>: peak/average power,
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
about the cost of the GPU itself. Amortized over any realistic life, the card
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
<table><thead><tr><th>GPU</th><th>OS</th><th>Python</th>
<th>Runs</th></tr></thead><tbody>
{% for e in envs %}
<tr><td>{{ e.gpu }}</td><td class="small">{{ e.os }}</td>
<td class="small">{{ e.python }}</td>
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
<p><strong>Experimental probes are kept separate and count toward nothing.</strong>
One-off experiments — like the spiral-window study on {% if dataset_key == "live" %}<a href="special.html">the
Special page</a>{% else %}the Special page{% endif %}, measuring how long each model takes to <em>start</em> answering —
run outside the dataset entirely. They never touch the leaderboard, discrimination,
or any model's score; they are a scratchpad, shown read-only for transparency.</p>
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
        key = (_html.escape(str(e.get("gpu") or "—")),
               _html.escape(str(e.get("os") or "—")),
               _html.escape(str(e.get("python") or "—")))
        env_counts[key] = env_counts.get(key, 0) + 1
    envs = [{"gpu": g, "os": o, "python": p, "n": n}
            for (g, o, p), n in sorted(env_counts.items(),
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
    host_list = [_html.escape(str(h))
                 for h, _ in sorted(hosts.items(), key=lambda kv: -kv[1])]

    mirror_ctx = None
    if dataset_key == "live":
        try:
            from .mirror import mirror_state
            mirror_ctx = mirror_state(_td)
        except Exception:
            mirror_ctx = None

    return _compiled(INFO_TEMPLATE).render(
        cost_note=cost_note(),
        nav=_nav(""), brand=_brand(""),
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
        mirror=mirror_ctx,
        dataset_label=dataset_label, dataset_key=dataset_key,
        n_tasks=len(tasks), n_models=n_models, n_runs=len(runs),
        ss=ss,
        categories=cats,
        lanes=LANE_BLURBS,
        metrics=METRIC_GLOSSARY,
        statuses=STATUS_GLOSSARY,
        caveats=(CAVEATS if dataset_key == "live" else
                [(t, b.replace('<a href="special.html">Special</a>',
                               "Special")) for t, b in CAVEATS]),
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


TOP_COHORT = 8

HARD_FLAGS = ("discriminator", "floor-gate")


def discrimination_stats(runs: list[dict], tdefs: dict) -> dict:
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
    k = (min(TOP_COHORT, len(ranked) // 2) if len(ranked) >= 6
         else max(1, len(ranked) // 2) if len(ranked) >= 2
         else 1)
    top, bot = set(ranked[:k]), set(ranked[-k:])
    top_spread = ((means[ranked[0]] - means[ranked[k - 1]])
                  if len(ranked) >= k >= 1 and ranked else 0.0)

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
        elif top_mean is not None and top_mean < 0.75:
            flag = "frontier"
        elif top_mean is not None and top_mean < 0.85:
            flag = "discriminator"
        elif sd >= 0.28 and 0.2 <= mean <= 0.85:
            flag = "discriminator"
        elif pct1 >= 0.7:
            flag = "ceiling"
        elif gap is not None and gap > 0.3:
            flag = "floor-gate"
        elif top_mean is not None and top_mean >= 0.95:
            flag = "ceiling"
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

    per_model_scores = {(m, tid): sc
                        for tid, sc in tvecs.items()
                        for m, sc in ((m, v) for m, v in sc.items())}
    hard = [r["tid"] for r in rows if r["flag"] in HARD_FLAGS]
    frontier = [r["tid"] for r in rows if r["flag"] == "frontier"]
    easy = [r["tid"] for r in rows if r["flag"] in ("ceiling", "dead")]
    grank = {m: r for m, r in zip(ranked, _competition_ranks(
        [means[m] for m in ranked]))}

    def _rank_on(subset: list[str]) -> list[dict]:
        bucket: dict[str, list[float]] = {}
        for tid in subset:
            for m, e in td[tid]["agg"].items():
                if e["score"].get("status") == "scored":
                    bucket.setdefault(m, []).append(e["score"]["score"])
        n_sub = len(subset) or 1
        rows_ = [{"model": m, "mean": sum(v) / len(v), "n": len(v),
                  "cover": f"{len(v)}/{n_sub}", "partial": len(v) < n_sub,
                  "global": means.get(m)} for m, v in bucket.items()]
        full = sorted((r for r in rows_ if not r["partial"]), key=lambda x: -x["mean"])
        part = sorted((r for r in rows_ if r["partial"]),
                      key=lambda x: (-x["n"], -x["mean"]))
        ranks = _competition_ranks([r["mean"] for r in full])
        counts: dict[int, int] = {}
        for rk in ranks:
            counts[rk] = counts.get(rk, 0) + 1
        for r, rk in zip(full, ranks):
            gi = grank.get(r["model"])
            r["rank"] = rk
            r["tied"] = counts[rk] > 1
            r["tied_with"] = counts[rk]
            r["delta"] = (gi - rk) if gi is not None else None
        for r in part:
            r.update({"rank": None, "tied": False, "tied_with": 1, "delta": None})
        return full + part

    hard_rank = _rank_on(hard)
    easy_rank = _rank_on(easy)
    frontier_rank = _rank_on(frontier)

    return {
        "rows": rows,
        "clusters": clusters,
        "hard_subset": hard,
        "hard_rank": hard_rank,
        "frontier_subset": frontier,
        "frontier_rank": frontier_rank,
        "easy_subset": easy,
        "easy_rank": easy_rank,
        "per_model_scores": per_model_scores,
        "top_spread": top_spread,
        "cohort_k": k,
        "top_models": ranked[:k],
        "bot_models": ranked[-k:],
        "n_tasks": len(rows),
        "n_dead": sum(1 for r in rows if r["flag"] == "dead"),
        "n_ceiling": sum(1 for r in rows if r["flag"] == "ceiling"),
        "n_frontier": sum(1 for r in rows if r["flag"] == "frontier"),
        "n_unbucketed": sum(1 for r in rows if r["flag"] not in
                            HARD_FLAGS + ("frontier", "ceiling", "dead")),
        "unbucketed": sorted(r["tid"] for r in rows if r["flag"] not in
                             HARD_FLAGS + ("frontier", "ceiling", "dead")),
        "n_discriminator": sum(1 for r in rows
                               if r["flag"] in ("discriminator", "frontier")),
        "mean_sd": (sum(r["sd"] for r in rows) / len(rows)) if rows else 0.0,
    }


def _competition_ranks(values: list[float], places: int = 4) -> list[int]:
    out: list[int] = []
    prev = None
    for i, v in enumerate(values):
        key = round(v, places)
        if prev is not None and key == prev:
            out.append(out[-1])
        else:
            out.append(i + 1)
        prev = key
    return out


def task_tiers(runs: list[dict] | None = None,
               tdefs: dict | None = None) -> dict[str, str]:
    runs = load_all_runs() if runs is None else runs
    tdefs = _task_defs() if tdefs is None else tdefs
    ds = discrimination_stats(runs, tdefs)
    out: dict[str, str] = {}
    for t in ds.get("easy_subset", []):
        out[t] = "easy"
    for t in ds.get("hard_subset", []):
        out[t] = "hard"
    for t in ds.get("frontier_subset", []):
        out[t] = "frontier"
    return out


HARDENED_TIERS = ("hard", "frontier")


def hardened_ids(tiers: dict[str, str] | None = None) -> list[str]:
    tiers = task_tiers() if tiers is None else tiers
    return sorted(t for t, v in tiers.items() if v in HARDENED_TIERS)


def is_hardened(tid: str, tiers: dict[str, str]) -> bool:
    return tiers.get(tid) in HARDENED_TIERS


def hardened_from_stats(ds: dict) -> set[str]:
    return set(ds.get("hard_subset", ())) | set(ds.get("frontier_subset", ()))


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
.whosbest th.tasks, .whosbest td.tasks { padding-left:18px; vertical-align:middle; }
.whosbest .tasks .mx-cells { border:0; height:auto; padding:3px 0; }
.whosbest th.tasks { font-weight:600; white-space:nowrap; }
.whosbest tr.fleetrow td { border-top:1px solid var(--rule); color:var(--muted); }
.whosbest tr.partialrow td { opacity:.62; }
.whosbest .pcov { font-size:9.5px; padding:0 4px; border-radius:6px;
  border:1px solid var(--warn); color:var(--warn); vertical-align:middle;
  opacity:1; }
</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>LLM Testing</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}task
  discrimination · suite v{{ suite_version }}</div></div>
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
<tr{% if h.partial %} class="partialrow" data-partial="1"{% endif %}><td class="num">{{ h.rank }}{% if h.tied %}<span class="note" style="font-size:10px"
  title="{{ h.tied_with }} models share this exact score — they are tied, not ordered. Any apparent order between them is arbitrary; separate them on speed or cost instead.">=</span>{% endif %}</td><td class="nowrap">{{ h.model }}{% if h.partial %} <span class="pcov"
  title="scored only {{ h.cover }} of this subset, so it is not ranked against models that completed all of it — the mean of a partial row is not comparable to a full one">{{ h.cover }}</span>{% endif %}</td>
<td class="num" data-sort="{{ h.mean_v }}">{{ h.mean }}</td>
<td class="num">{{ h.glob }}</td><td class="num">{{ h.move }}</td>
{% if s.cats %}<td class="tasks"><div class="mx-cells">{% for g in h.groups %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div></td>{% endif %}</tr>
{% endfor %}
{% if s.cats %}<tr class="fleetrow"><td></td><td class="nowrap small">fleet avg / task →</td><td></td><td></td><td></td>
<td class="tasks"><div class="mx-cells">{% for g in s.foot %}<div class="mx-grp">{% for cell in g %}<a class="mx-cell {{ cell.cls }}"{% if cell.cls == 'pass' %} style="--a:{{ cell.a }}"{% endif %} href="{{ cell.href }}" title="{{ cell.tip }}"></a>{% endfor %}</div>{% endfor %}</div></td></tr>{% endif %}
</table></div>
<p class="note" style="margin-top:4px">{{ label }} subset ({{ s.n }}): {{ s.tasks }}</p>
{% endmacro %}

{% if hard.rank or easy.rank or frontier.rank %}
<h2>Who's actually best — ranked on a task subset</h2>
<p class="note">The global leaderboard is inflated by tasks everyone aces.
These are three <b>disjoint</b> tiers, derived live from how models actually
scored — no task appears in two. <b>Frontier</b> is the hardest: even the top
cohort still struggles, so this is where the leaders get separated from each
other. <b>Hard</b> is the middle: wide-spread discriminators that split the
field, though the best mostly clear them. <b>Easy</b> is the other end — the
tasks almost every model gets right; the ranking there is <em>supposed</em> to be
flat, and seeing it collapse is the point. <b>Move</b> is the shift vs the global
rank: <span style="color:#3a3">▲climbs</span> = stronger on that subset than its
overall score suggests, <span style="color:#c55">▼drops</span> = was riding the
other end.</p>
<div class="seg" id="sbseg">
  <button type="button" data-sb="hard" class="on">◆ Hard ({{ hard.n }})</button>
  <button type="button" data-sb="frontier">◆ Frontier ({{ frontier.n }})</button>
  <button type="button" data-sb="easy">◆ Easy ({{ easy.n }})</button>
</div>
<div id="sb-hard">{{ standings(hard, 'Hard') }}</div>
<div id="sb-frontier" style="display:none">{{ standings(frontier, 'Frontier') }}</div>
<div id="sb-easy" style="display:none">{{ standings(easy, 'Easy') }}</div>
<script>
document.querySelectorAll('#sbseg button').forEach(b =>
  b.addEventListener('click', () => {
    document.querySelectorAll('#sbseg button').forEach(x => x.classList.toggle('on', x === b));
    ['frontier', 'hard', 'easy'].forEach(k => {
      const el = document.getElementById('sb-' + k);
      if (el) el.style.display = b.dataset.sb === k ? '' : 'none';
    });
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
        rank = [{"rank": h.get("rank") or "—",
                 "tied": h.get("tied", False),
                 "tied_with": h.get("tied_with", 1),
                 "partial": h.get("partial", False),
                 "cover": h.get("cover", ""),
                 "model": _mlink(h["model"]),
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
    frontier = _standings(d["frontier_subset"], d["frontier_rank"])

    return _compiled(DISCRIMINATE_TEMPLATE).render(
        hard=hard, easy=easy, frontier=frontier,
        nav=_nav(""), brand=_brand(""),
        sort_js=_SORT_JS, css=BASE_CSS, tiles=tiles, rows=trows,
        clusters=clusters, legend=legend,
        top_models=", ".join(d["top_models"]),
        bot_models=", ".join(d["bot_models"]),
        cohort_k=d["cohort_k"], top_spread=f"{d['top_spread']:.2f}",
        dataset_label=dataset_label, dataset_key=dataset_key,
        suite_version=config.suite_version())



def family_stats(runs: list[dict], tdefs: dict) -> dict:
    from . import gguf
    from .registry import infer_family, load_models

    reg = _registry()
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
<div class="topbar">{{ brand }}<div class="ttl"><h1>LLM Testing</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">{% if dataset_label %}{{ dataset_label }} · {% endif %}model
  families · suite v{{ suite_version }}</div></div>
<div class="wrap">
<p class="note">Models grouped by lineage — so you can read a family's
<b>size↔capability ladder</b> and see how a small local model stacks up against
its larger hosted sibling. A <span class="pill2">local + hosted</span> tag marks
a family you can compare across that line. Family is set on the
<b>Organize</b> page (a yaml <code>family:</code> key), else inferred from the
name — a model placed in <b>No-family</b> doesn't appear here.</p>

{% if verscmp %}
<h2>Version-over-version</h2>
<div class="card vc-wrap">
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

    def _full(v):
        return [x for x in v if x.get("coverage", 0) >= 0.999] or []

    multi = {f: v for f, v in fams.items() if len(v) > 1}
    singles = sorted(f for f, v in fams.items() if len(v) == 1)
    fam_cards = []

    def _card_key(f):
        got = _full(multi[f])
        return -max((x["score"] for x in got), default=-1)

    for f in sorted(multi, key=_card_key):
        members = multi[f]
        has_both = len({x["local"] for x in members}) > 1
        got = _full(members)
        fam_cards.append({
            "name": f, "n": len(members),
            "span": (f"{min(x['score'] for x in got):.3f}–"
                     f"{max(x['score'] for x in got):.3f}" if got else "—"),
            "both": has_both, "rows": [fmt(x) for x in members],
        })

    champs = []
    for f, v in fams.items():
        got = _full(v)
        if not got:
            continue
        top = max(got, key=lambda x: x["score"])
        champs.append({"name": f, "best": top["score"],
                       "leader": _mlink(top["model"]), "n": len(got)})
    champs.sort(key=lambda c: -c["best"])
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
    return _compiled(FAMILY_TEMPLATE).render(
        nav=_nav(""), brand=_brand(""),
        sort_js=_SORT_JS, scatter_js=_SCATTER_HOVER_JS,
        verscmp=verscmp, verscmp_js=_VERSCMP_JS,
        css=BASE_CSS, fam_cards=fam_cards, champs=champs,
        size_chart=size_chart, singles=", ".join(singles),
        dataset_label=dataset_label, dataset_key=dataset_key,
        suite_version=config.suite_version())


COMPARE_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compare · LLM Testing</title><style>{{ css }}</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>Head to head</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">two models, every task, side by side · {{ dataset_label or "live dataset" }}</div></div>

<div class="cmp-pick">
  <span class="cmp-lead"></span>
  <select id="selA" class="cmp-sel"></select>
  <button id="swap" class="cmp-swap" title="swap sides">&#8646;</button>
  <select id="selB" class="cmp-sel"></select>
</div>

<div id="cmp-head" class="cmp-head"></div>
<h2>Per-task <span class="small muted" style="text-transform:none;letter-spacing:0;font-weight:400">· swatch ink ramps with the score · Δ colors the winner · grouped by category</span></h2>
<div id="cmp-grid"></div>
<div class="foot" style="margin-top:14px">{{ cost_note|safe }}</div>

<script>const D = {{ data_json|safe }};</script>
<script>
const $ = s => document.querySelector(s);
function q(v){
  return (0.10 + 0.90*Math.max(0,Math.min(1,v))).toFixed(3);
}
function sc(v){
  if (v === null || v === undefined)
    return {cls:'muted', txt:'\\u2014', sw:'<span class="hsw pend"></span>'};
  const st = v >= 0.8 ? 'good' : (v >= 0.4 ? 'warn' : 'crit');
  return {cls:st, txt:v.toFixed(3),
          sw:'<span class="hsw" style="--a:'+q(v)+'"></span>'};
}
function num(x){ return (x === null || x === undefined) ? null : x; }
function fmtPct(v){ return v === null ? '\\u2014' : Math.round(v*100)+'%'; }

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
  let h = '<div class="cmp-row cmp-hrow">'
        + '<span class="cmp-k"></span>'
        + '<span class="cmp-hc"><a href="models/'+A.slug+'.html">'+a+'</a>'
        + '<div class="small muted">#'+A.rank+' \\u00b7 '+A.where+'</div></span>'
        + '<span class="cmp-dc"></span>'
        + '<span class="cmp-hc"><a href="models/'+B.slug+'.html">'+b+'</a>'
        + '<div class="small muted">#'+B.rank+' \\u00b7 '+B.where+'</div></span></div>';
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
    h += '<div class="cmp-row">'
       + '<span class="cmp-k">'+label+'</span>'
       + '<span class="cmp-v '+wa+'">'+fmt(A)+'</span>'
       + '<span class="cmp-dc">'+(delta?'<span class="cmp-td">'+delta+'</span>':'')+'</span>'
       + '<span class="cmp-v '+wb+'">'+fmt(B)+'</span></div>';
  }
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
  const opts = D.names.map(m => '<option value="'+m+'">'+m+'</option>').join('');
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


def special_summary() -> dict:
    import re
    import statistics
    base = config.SPECIAL_DIR
    guard = config.CLAUDE_SPIRAL_S
    official = {t.id: t.timeout_s for t in _cached_tasks()}
    run_window: dict = {}
    if base.is_dir():
        for rj in base.glob("*/run.json"):
            m = re.search(r"spiral@(\d+)s", read_json(rj, {}).get("tag") or "")
            if m:
                run_window[rj.parent.name] = int(m.group(1))
    cells: dict = {}
    if base.is_dir():
        for mfile in base.glob("*/*/*/metrics.json"):
            run = mfile.parents[2].name
            if run not in run_window:
                continue
            model, task = mfile.parents[1].name, mfile.parent.name
            d = read_json(mfile, {})
            c = cells.setdefault((model, task), {
                "model": model, "task": task, "trials": 0, "answered": 0,
                "ttfa": [], "scores": [], "windows": set()})
            if run in run_window:
                c["windows"].add(run_window[run])
            c["trials"] += 1
            attempts = d.get("attempts") or [{}]
            ftm = next((a.get("first_text_ms") for a in attempts
                        if a.get("first_text_ms") is not None), None)
            if d.get("status") == "ok":
                c["answered"] += 1
                if ftm is not None:
                    c["ttfa"].append(ftm)
            sc = read_json(mfile.parent / "score.json", {})
            if sc.get("status") == "scored" and sc.get("score") is not None:
                c["scores"].append(sc["score"])
    def _win(ws):
        ws = sorted(ws)
        if not ws:
            return "—"
        return f"{ws[0]}s" if len(ws) == 1 else f"{ws[0]}–{ws[-1]}s"
    rows, all_ttfa, models = [], [], {}
    for c in cells.values():
        all_ttfa += c["ttfa"]
        rows.append({
            "model": c["model"], "task": c["task"], "trials": c["trials"],
            "answered": c["answered"], "window": _win(c["windows"]),
            "official_s": official.get(c["task"]),
            "ttfa_max_s": round(max(c["ttfa"]) / 1000, 1) if c["ttfa"] else None,
            "ttfa_med_s": (round(statistics.median(c["ttfa"]) / 1000, 1)
                           if c["ttfa"] else None),
            "score_avg": (round(sum(c["scores"]) / len(c["scores"]), 3)
                          if c["scores"] else None)})
        mm = models.setdefault(c["model"], {"model": c["model"], "probed": 0,
                                            "answered": 0, "ttfa": [], "scores": []})
        mm["probed"] += 1
        if c["answered"] > 0:
            mm["answered"] += 1
            mm["ttfa"] += c["ttfa"]
            mm["scores"] += c["scores"]
    rows.sort(key=lambda r: (r["model"], r["task"]))
    model_rows = []
    for mm in models.values():
        answered, probed = mm["answered"], mm["probed"]
        model_rows.append({
            "model": mm["model"], "probed": probed, "answered": answered,
            "needed_s": round(max(mm["ttfa"]) / 1000, 1) if mm["ttfa"] else None,
            "score_avg": (round(sum(mm["scores"]) / len(mm["scores"]), 3)
                          if mm["scores"] else None),
            "verdict": ("window-limited" if answered == probed
                        else "partial" if answered else "never answers")})
    model_rows.sort(key=lambda r: (-(r["needed_s"] or 0), r["model"]))

    tasks: dict = {}
    for c in cells.values():
        t = tasks.setdefault(c["task"], {"task": c["task"], "ttfa": [],
                                         "models": set(),
                                         "official_s": official.get(c["task"])})
        t["ttfa"] += c["ttfa"]
        t["models"].add(c["model"])
    task_rows = []
    for t in tasks.values():
        widest = round(max(t["ttfa"]) / 1000, 1) if t["ttfa"] else None
        task_rows.append({
            "task": t["task"], "official_s": t["official_s"],
            "models": len(t["models"]), "widest_s": widest,
            "over": (widest is not None and t["official_s"] is not None
                     and widest > t["official_s"])})
    task_rows.sort(key=lambda r: -(r["widest_s"] or 0))

    return {"rows": rows, "models": model_rows, "tasks": task_rows,
            "guard_s": guard,
            "window_needed_s": round(max(all_ttfa) / 1000, 1) if all_ttfa else None}


def special_turns_summary() -> dict:
    import re
    import statistics
    from . import assess
    base = config.SPECIAL_DIR
    thr = assess.load_cfg().get("pass_threshold", 0.8)
    run_cap: dict = {}
    if base.is_dir():
        for rj in base.glob("*/run.json"):
            m = re.search(r"turns@(\d+)", read_json(rj, {}).get("tag") or "")
            if m:
                run_cap[rj.parent.name] = int(m.group(1))
    cells: dict = {}
    if base.is_dir():
        for mfile in base.glob("*/*/*/metrics.json"):
            run = mfile.parents[2].name
            if run not in run_cap:
                continue
            model, task = mfile.parents[1].name, mfile.parent.name
            c = cells.setdefault((model, task), {
                "model": model, "task": task, "trials": 0, "turns": [],
                "scores": [], "caps": set(), "finished": 0})
            d = read_json(mfile, {})
            c["caps"].add(run_cap[run])
            c["trials"] += 1
            if d.get("turns") is not None:
                c["turns"].append(d["turns"])
            if d.get("status") != "max_turns":
                c["finished"] += 1
            sc = read_json(mfile.parent / "score.json", {})
            if sc.get("status") == "scored" and sc.get("score") is not None:
                c["scores"].append(sc["score"])

    def _cap(cs):
        cs = sorted(cs)
        return "—" if not cs else (str(cs[0]) if len(cs) == 1
                                   else f"{cs[0]}–{cs[-1]}")

    def _verdict(savg):
        if savg is None:
            return "no score"
        if savg >= thr:
            return "converged"
        return "improved" if savg > 0 else "still stuck"

    rows, models, tasks = [], {}, {}
    for c in cells.values():
        savg = (round(sum(c["scores"]) / len(c["scores"]), 3)
                if c["scores"] else None)
        rows.append({
            "model": c["model"], "task": c["task"], "trials": c["trials"],
            "cap": _cap(c["caps"]),
            "turns_max": max(c["turns"]) if c["turns"] else None,
            "turns_med": round(statistics.median(c["turns"])) if c["turns"] else None,
            "finished": c["finished"], "score_avg": savg,
            "verdict": _verdict(savg)})
        mm = models.setdefault(c["model"], {"model": c["model"], "probed": 0,
                                            "converged": 0, "scores": []})
        mm["probed"] += 1
        if savg is not None:
            mm["scores"].append(savg)
            if savg >= thr:
                mm["converged"] += 1
        tt = tasks.setdefault(c["task"], {"task": c["task"], "models": set(),
                                          "converged": 0, "turns": []})
        tt["models"].add(c["model"])
        tt["turns"] += c["turns"]
        if savg is not None and savg >= thr:
            tt["converged"] += 1
    rows.sort(key=lambda r: (r["model"], r["task"]))
    model_rows = [{
        "model": mm["model"], "probed": mm["probed"], "converged": mm["converged"],
        "score_avg": (round(sum(mm["scores"]) / len(mm["scores"]), 3)
                      if mm["scores"] else None),
        "verdict": ("turn-limited" if mm["converged"] == mm["probed"]
                    else "partly turn-limited" if mm["converged"]
                    else "genuinely stuck")}
        for mm in models.values()]
    model_rows.sort(key=lambda r: (-r["converged"], r["model"]))
    task_rows = [{
        "task": tt["task"], "models": len(tt["models"]),
        "converged": tt["converged"],
        "turns_typ": (round(statistics.median(tt["turns"]))
                      if tt["turns"] else None)}
        for tt in tasks.values()]
    task_rows.sort(key=lambda r: -r["converged"])
    return {"rows": rows, "models": model_rows, "tasks": task_rows}


def special_budget_summary() -> dict:
    import re
    import statistics
    from . import assess
    base = config.SPECIAL_DIR
    thr = assess.load_cfg().get("pass_threshold", 0.8)
    run_budget: dict = {}
    if base.is_dir():
        for rj in base.glob("*/run.json"):
            m = re.search(r"budget@(\d+)", read_json(rj, {}).get("tag") or "")
            if m:
                run_budget[rj.parent.name] = int(m.group(1))
    cells: dict = {}
    if base.is_dir():
        for mfile in base.glob("*/*/*/metrics.json"):
            run = mfile.parents[2].name
            if run not in run_budget:
                continue
            model, task = mfile.parents[1].name, mfile.parent.name
            c = cells.setdefault((model, task), {
                "model": model, "task": task, "trials": 0, "budgets": set(),
                "scores": [], "spoke": 0, "visible": []})
            d = read_json(mfile, {})
            c["budgets"].add(run_budget[run])
            c["trials"] += 1
            atts = d.get("attempts") or []
            vis = max(((a.get("tokens_out") or 0) - (a.get("reasoning_tokens") or 0)
                       for a in atts), default=0)
            c["visible"].append(vis)
            from .runner import BUDGET_MUTE_TOKENS
            if vis > BUDGET_MUTE_TOKENS:
                c["spoke"] += 1
            sc = read_json(mfile.parent / "score.json", {})
            if sc.get("status") == "scored" and sc.get("score") is not None:
                c["scores"].append(sc["score"])

    def _span(xs):
        xs = sorted(xs)
        return "—" if not xs else (f"{xs[0]:,}" if len(xs) == 1
                                  else f"{xs[0]:,}–{xs[-1]:,}")

    rows, models = [], {}
    for c in cells.values():
        savg = (round(sum(c["scores"]) / len(c["scores"]), 3)
                if c["scores"] else None)
        spoke = c["spoke"] > 0
        verdict = ("still mute" if not spoke
                   else "converted" if savg is not None and savg >= thr
                   else "spoke, partial" if savg else "spoke, still wrong")
        rows.append({
            "model": c["model"], "task": c["task"], "trials": c["trials"],
            "budget": _span(c["budgets"]),
            "visible_max": max(c["visible"]) if c["visible"] else None,
            "visible_med": (round(statistics.median(c["visible"]))
                            if c["visible"] else None),
            "spoke": c["spoke"], "score_avg": savg, "verdict": verdict})
        mm = models.setdefault(c["model"], {"model": c["model"], "probed": 0,
                                            "spoke": 0, "converted": 0,
                                            "scores": []})
        mm["probed"] += 1
        if spoke:
            mm["spoke"] += 1
        if savg is not None:
            mm["scores"].append(savg)
            if savg >= thr:
                mm["converted"] += 1
    rows.sort(key=lambda r: (r["model"], r["task"]))
    model_rows = [{
        "model": mm["model"], "probed": mm["probed"], "spoke": mm["spoke"],
        "converted": mm["converted"],
        "score_avg": (round(sum(mm["scores"]) / len(mm["scores"]), 3)
                      if mm["scores"] else None),
        "verdict": ("budget-limited" if mm["converted"] == mm["probed"]
                    else "partly budget-limited" if mm["converted"]
                    else "speaks but wrong" if mm["spoke"]
                    else "never converges")}
        for mm in models.values()]
    model_rows.sort(key=lambda r: (-r["converted"], -r["spoke"], r["model"]))
    return {"rows": rows, "models": model_rows}


SPECIAL_STATIC_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Special · LLM Testing</title><style>{{ css }}
.exp { background:var(--surface); border-left:3px solid var(--trap); border-radius:6px;
  padding:12px 16px; margin:14px 0 22px; font-size:12.5px; color:var(--ink-2); }
.exp b { color:var(--trap); }
.headline { font-size:15px; margin:0 0 20px; } .headline b { color:var(--good); font-size:20px; }
.sp-tbl { border-collapse:collapse; width:100%; font-size:13px; margin-bottom:8px; }
.sp-tbl th, .sp-tbl td { padding:6px 10px; border-bottom:1px solid var(--hair); text-align:left; }
.sp-tbl th { color:var(--muted); font-weight:600; }
.sp-tbl td.n, .sp-tbl th.n { text-align:right; font-variant-numeric:tabular-nums;
  font-family:var(--mono); }
tr.grp td { font-weight:700; color:var(--ink); background:var(--surface); padding-top:8px; }
</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>Special — experiments</h1></div>
<div class="nav">{{ nav }}</div></div>
<div class="pagebar"><div class="sub">read-only findings · {{ dataset_label or "live dataset" }}</div></div>
<div class="exp"><b>EXPERIMENTAL — not part of any dataset.</b> These runs count
toward <b>nothing</b> — not the leaderboard, not discrimination, not any model's
score. A scratchpad for probes into how models behave at the edges. Every probe
run ships with the repository under <code>special/</code>, one directory per run,
with the same per-cell <code>metrics.json</code>, <code>score.json</code> and
transcript as a scored run — so every number below can be checked against the
calls that produced it.</div>

{% if rows %}
<h2>Spiral / rumination window probe</h2>
<p class="small muted">How long each model takes to <em>start answering</em>
(time-to-first-answer-token) on the tasks where it hit the suite's no-output
guard. A model over the guard was being cut off — a slow starter, not
necessarily incapable.</p>
{% if tasks %}
<h2>By task — window needed vs the official budget</h2>
<p class="small muted">For each test we have probe data on: the widest window
<em>any</em> model needed to start answering, against that test's official suite
timeout. "over" means at least one model can't begin inside the real budget.</p>
<table class="sp-tbl"><tr><th>Task</th><th class="n">models tested</th>
<th class="n">widest window needed</th><th class="n">official budget</th>
<th class="n">headroom</th></tr>
{% for t in tasks %}
<tr><td>{{ t.task }}</td><td class="n">{{ t.models }}</td>
<td class="n">{% if t.widest_s is none %}—{% else %}{{ t.widest_s }}s{% endif %}</td>
<td class="n">{% if t.official_s is none %}—{% else %}{{ t.official_s }}s{% endif %}</td>
<td class="n">{% if t.widest_s is none or t.official_s is none %}—{% elif t.over %}<span style="color:var(--crit)">−{{ (t.widest_s - t.official_s)|round|int }}s over</span>{% else %}<span style="color:var(--good)">+{{ (t.official_s - t.widest_s)|round|int }}s</span>{% endif %}</td></tr>
{% endfor %}
</table>
{% endif %}

<h2>Per model</h2>
<table class="sp-tbl"><tr><th>Model</th><th class="n">answered</th>
<th class="n">window needed</th><th class="n">vs {{ guard_s }}s</th>
<th class="n">score</th><th>verdict</th></tr>
{% for m in models %}
<tr><td>{{ m.model }}</td><td class="n">{{ m.answered }}/{{ m.probed }}</td>
<td class="n">{% if m.needed_s is none %}—{% else %}{{ m.needed_s }}s{% endif %}</td>
<td class="n">{% if m.needed_s is none %}—{% elif m.needed_s > guard_s %}+{{ (m.needed_s - guard_s)|round|int }}s{% else %}fits{% endif %}</td>
<td class="n">{% if m.score_avg is none %}—{% else %}{{ m.score_avg }}{% endif %}</td>
<td style="font-weight:600;color:{{ 'var(--good)' if m.verdict=='window-limited' else 'var(--crit)' if m.verdict=='never answers' else 'var(--warn)' }}">{{ m.verdict }}</td></tr>
{% endfor %}
</table>

<h2>Per model · per test</h2>
<table class="sp-tbl"><tr><th>Model / task</th>
<th class="n">official budget</th><th class="n">probe window</th>
<th class="n">answered</th><th class="n">first answer</th><th class="n">vs official</th>
<th class="n">typical</th><th class="n">score</th></tr>
{% for r in rows %}{% if r.show_model %}<tr class="grp"><td colspan="8">{{ r.model }}</td></tr>{% endif %}
<tr><td style="padding-left:18px">{{ r.task }}</td>
<td class="n">{% if r.official_s is none %}—{% else %}{{ r.official_s }}s{% endif %}</td>
<td class="n">{{ r.window }}</td>
<td class="n">{{ r.answered }}/{{ r.trials }}</td>
<td class="n">{% if r.ttfa_max_s is none %}—{% else %}{{ r.ttfa_max_s }}s{% endif %}</td>
<td class="n">{% if r.ttfa_max_s is none or r.official_s is none %}—{% elif r.ttfa_max_s > r.official_s %}<span style="color:var(--crit)">+{{ (r.ttfa_max_s - r.official_s)|round|int }}s over</span>{% else %}fits{% endif %}</td>
<td class="n">{% if r.ttfa_med_s is none %}—{% else %}{{ r.ttfa_med_s }}s{% endif %}</td>
<td class="n">{% if r.score_avg is none %}—{% else %}{{ r.score_avg }}{% endif %}</td></tr>
{% endfor %}
</table>
<p class="small muted"><b>official budget</b> = the real suite timeout for that
test (what the model must fit in when it counts). <b>first answer</b> = slowest
time-to-first-answer in the probe. <b>vs official</b>: "over" means it can't
start answering inside the test's real budget; "fits" means it can.</p>
{% endif %}

{% if turns.models %}
<h2>Turn-budget probe <span class="muted" style="font-weight:400">· agentic loops</span></h2>
<p class="small muted">An agentic task ends when the tool-use loop runs out of
turns, which is our cap and not the model's ability. These cells were re-run with
a raised cap to find out which it was. <b>turn-limited</b> = every probed cell
passed once the cap moved, so the recorded 0 was our limit.</p>
<table class="sp-tbl"><tr><th>Model</th><th class="n">cells probed</th>
<th class="n">converged</th><th class="n">score</th><th>verdict</th></tr>
{% for m in turns.models %}
<tr><td>{{ m.model }}</td><td class="n">{{ m.probed }}</td>
<td class="n">{{ m.converged }}/{{ m.probed }}</td>
<td class="n">{% if m.score_avg is none %}—{% else %}{{ m.score_avg }}{% endif %}</td>
<td>{{ m.verdict }}</td></tr>
{% endfor %}
</table>
{% endif %}

{% if budget.models %}
<h2>Token-budget probe <span class="muted" style="font-weight:400">· the model never got to speak</span></h2>
<p class="small muted">A thinking model can spend its whole output budget in the
think channel and emit almost nothing a checker can read. Scoring that 0 records
"cannot do the task" when what was seen is "was not given room to say so". These
cells were re-run with the ceiling raised. <b>budget-limited</b> = every probed
cell passed at a larger budget, so the published 0 was our ceiling;
<b>speaks but wrong</b> = it needed room and was still wrong.</p>
<table class="sp-tbl"><tr><th>Model</th><th class="n">cells probed</th>
<th class="n">spoke</th><th class="n">converted</th><th class="n">score</th>
<th>verdict</th></tr>
{% for m in budget.models %}
<tr><td>{{ m.model }}</td><td class="n">{{ m.probed }}</td>
<td class="n">{{ m.spoke }}/{{ m.probed }}</td>
<td class="n">{{ m.converted }}/{{ m.probed }}</td>
<td class="n">{% if m.score_avg is none %}—{% else %}{{ m.score_avg }}{% endif %}</td>
<td>{{ m.verdict }}</td></tr>
{% endfor %}
</table>
{% endif %}

{% if th_rows %}
<h2>Thinking-off probe <span class="muted" style="font-weight:400">· what does reasoning buy, and what does it cost?</span></h2>
<p class="small muted">Most models reason by default and nothing in a scored run
controls that. Each cell below was run <b>twice in the same job</b> — reasoning
on, then off — so the pair is matched on sampling and task content. Nothing here
touches a model's score.</p>
<p class="small muted"><b>Read the verdict, not the token saving.</b>
<span style="color:#3a3">free saving</span> = the score held and the tokens
dropped, so reasoning was paid for and unused on that test.
<span style="color:#c33">thinking required</span> = disabling it cost score, so
reasoning is load-bearing. <span style="color:#96c">not applied</span> = the
provider accepted the flag and kept reasoning anyway, so that row measures
nothing about reasoning — only about the provider.
<span style="color:var(--muted)">nothing to disable</span> = the model barely
reasoned on that test to begin with, so whether the flag landed cannot be read
from the tokens; that is our blind spot, not the provider's fault.</p>
<table class="sp-tbl"><tr><th>Model</th><th>Test</th><th class="n">n</th>
<th class="n">score on→off</th><th class="n">output tokens</th>
<th class="n">tok saved</th><th class="n">reasoning on→off</th>
<th class="n">cost saved</th><th>verdict</th></tr>
{% for r in th_rows %}
<tr><td>{{ r.model }}</td><td>{{ r.task }}</td>
<td class="n">{{ [r.n_on, r.n_off]|min }}</td>
<td class="n">{{ "%.2f"|format(r.score_on) }}→{{ "%.2f"|format(r.score_off) }}</td>
<td class="n">{{ r.out_on|round|int }}→{{ r.out_off|round|int }}</td>
<td class="n">{% if r.out_saved_pct is none %}—{% else %}{{ r.out_saved_pct }}%{% endif %}</td>
<td class="n">{{ r.reas_on|round|int }}→{{ r.reas_off|round|int }}</td>
<td class="n">{% if not r.cost_on %}—{% else %}{{ ((1 - r.cost_off / r.cost_on) * 100)|round|int }}%{% endif %}</td>
<td>{{ r.verdict }}</td></tr>
{% endfor %}
</table>

{% if th_cost.models %}
<h2>Thinking-off cost analysis <span class="muted" style="font-weight:400">· counted only where the score held</span></h2>
<p class="small muted">A saving bought by getting the answer wrong is not a
saving, so cost is credited only on cells verdicted <b>free saving</b>. A
provider that ignored the flag earns none of it while still being billed for the
calls. These figures are for these tests only and are <b>not</b> extrapolated to
the suite — the candidates were chosen for being mechanical, which is exactly
where the saving is largest.</p>
<table class="sp-tbl"><tr><th>Model</th><th class="n">cells</th>
<th class="n">flag applied</th><th class="n">free saving</th>
<th class="n">thinking required</th><th class="n">cost saved where free</th>
<th class="n">%</th><th class="n">probe cost</th></tr>
{% for m in th_cost.models %}
<tr><td>{{ m.model }}</td><td class="n">{{ m.cells }}</td>
<td class="n">{{ m.applied }}/{{ m.cells }}</td>
<td class="n" style="color:#3a3">{{ m.free }}</td>
<td class="n" style="color:#c33">{{ m.required }}</td>
<td class="n">${{ "%.5f"|format(m.free_cost_saved) }}</td>
<td class="n">{% if m.free_cost_saved_pct is none %}—{% else %}{{ m.free_cost_saved_pct }}%{% endif %}</td>
<td class="n muted">${{ "%.5f"|format(m.probe_cost) }}</td></tr>
{% endfor %}
</table>
<p class="small muted">Across {{ th_cost.total.cells }} paired cell(s):
<b>{{ th_cost.total.free }}</b> free saving, <b>{{ th_cost.total.required }}</b>
thinking required, <b>{{ th_cost.total.cells - th_cost.total.applied }}</b> where
the provider did not apply the flag. Saved
<b>${{ "%.5f"|format(th_cost.total.free_cost_saved) }}</b> of
${{ "%.5f"|format(th_cost.total.free_cost_on) }} on the cells that held their
score{% if th_cost.total.free_cost_saved_pct is not none %}
(<b>{{ th_cost.total.free_cost_saved_pct }}%</b>){% endif %}. Measuring it cost
<b>${{ "%.5f"|format(th_cost.total.probe_cost) }}</b>{% if th_cost.total.payback_runs is not none %},
so the probe pays for itself after <b>{{ th_cost.total.payback_runs }}</b> sweeps
of these tests{% endif %}. A row below n={{ th_cost.n_floor }} reads "needs
repeats": the token delta is stable at one trial, a score delta is not.</p>
{% endif %}

{% if th_support %}
<h2>Which providers can even be asked <span class="muted" style="font-weight:400">· measured, not read off a capability list</span></h2>
<p class="small muted">Support is tested per provider rather than trusted:
several models advertise a reasoning parameter and then refuse to disable it, and
at least one accepts the flag, returns success, and keeps reasoning anyway. A
provider that refuses is skipped with nothing written — never scored 0. Local
models are excluded on measurement: LM Studio accepts a parameter that does not
exist and left reasoning unchanged, so an unsupported knob there cannot be
detected by asking.</p>
<table class="sp-tbl"><tr><th>Model</th><th>Verdict</th><th>What the provider did</th></tr>
{% for s in th_support %}
<tr><td>{{ s.model }}</td><td>{{ s.verdict }}</td>
<td class="muted">{{ s.detail }}</td></tr>
{% endfor %}
</table>
{% endif %}

<h2>Which tests were eligible <span class="muted" style="font-weight:400">· and why these</span></h2>
<p class="small muted">Only mechanical work is a fair candidate. Derivation tasks
are excluded because reasoning <em>is</em> the task there, and the app-building
tasks because their output is dominated by code, so reasoning is a small fraction
of it.</p>
<table class="sp-tbl"><tr><th>Test</th><th>Why it was a candidate</th></tr>
{% for tid, why in th_candidates.items() %}
<tr><td>{{ tid }}</td><td class="muted">{{ why }}</td></tr>
{% endfor %}
</table>
{% endif %}

{% if not any_output %}
<p class="muted">No experimental results yet.</p>
{% endif %}
<div class="css-tie" style="color:var(--accent)"></div>
</body></html>"""


PROBE_KINDS = ("spiral", "turns", "budget", "thinking", "apicost")


def probe_counts() -> dict:
    from . import thinking
    out: dict = {k: {} for k in PROBE_KINDS}

    def put(kind, model, task, n):
        out[kind].setdefault(model, {})[task] = n

    for r in special_summary().get("rows") or []:
        put("spiral", r["model"], r["task"], r.get("trials") or 0)
    for r in special_turns_summary().get("rows") or []:
        put("turns", r["model"], r["task"], r.get("trials") or 0)
    for r in special_budget_summary().get("rows") or []:
        put("budget", r["model"], r["task"], r.get("trials") or 0)
    for r in thinking.results():
        put("thinking", r["model"], r["task"],
            min(r.get("n_on") or 0, r.get("n_off") or 0))
    from . import apicost
    for r in apicost.results():
        put("apicost", r["compare_key"], r["task"], r.get("trials") or 0)
    return out


def probe_missing(kind: str, model: str, tasks, target: int,
                  counts: dict | None = None) -> dict:
    have = (counts if counts is not None else probe_counts()).get(kind, {})
    have = have.get(model, {})
    return {t: max(0, int(target) - int(have.get(t, 0))) for t in tasks}


LINKS_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Links · Token Waster</title><style>{{ css }}
.lk-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  gap:12px; margin:18px 0 26px; }
.lk { display:flex; align-items:center; gap:14px; padding:16px 18px;
  background:var(--surface); border:1px solid var(--hair); border-radius:10px;
  color:var(--ink); text-decoration:none; }
.lk:hover { border-color:var(--accent); text-decoration:none;
  background:var(--surface-2); }
.lk svg { width:26px; height:26px; flex:none; color:var(--muted); }
.lk:hover svg { color:var(--brand); }
.lk .n { font-weight:650; font-size:15px; }
.lk .h { color:var(--muted); font-size:12.5px; }
.lk-hero { font-size:15px; color:var(--ink-2); max-width:70ch; margin:0 0 4px; }
.lk-stat { display:flex; gap:26px; flex-wrap:wrap; margin:6px 0 22px;
  font-size:12.5px; color:var(--muted); }
.lk-stat b { color:var(--ink); font-size:15px; font-family:var(--mono); }
</style></head><body>
<div class="topbar">{{ brand }}<div class="ttl"><h1>Links</h1></div>
<div class="nav">{{ nav }}</div></div>

<p class="lk-hero">I run a real benchmark harness on camera and publish the
receipts — including when it says I was wrong. Everything below is the same
project from a different angle.</p>
<div class="lk-stat">
  <span><b>{{ n_models }}</b> models</span>
  <span><b>{{ n_tasks }}</b> tasks</span>
  <span><b>{{ n_runs }}</b> runs on record</span>
  <span>suite <b>v{{ suite_version }}</b></span>
</div>

<div class="lk-grid">
<a class="lk" href="index.html">
  {{ brand_svg }}
  <span><span class="n">The leaderboard</span><br>
  <span class="h">every model, every task, with the transcripts</span></span></a>
{% for s in socials %}
<a class="lk" href="{{ s.url }}" target="_blank" rel="noopener me"
   style="--brand:{{ s.colour }}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor"
    d="{{ s.path }}"/></svg>
  <span><span class="n">{{ s.name }}</span><br>
  <span class="h">{{ s.handle }}</span></span></a>
{% endfor %}
</div>

<div class="foot">Scores are the mean of every scored run per model·task, so
re-running a model fleshes its number out rather than replacing it. A model that
has not attempted the whole suite is shown but never ranked — its mean is not
comparable. <a href="info.html">How the scoring works →</a></div>
</body></html>"""


def build_links_page(runs: list[dict], tdefs: dict) -> str:
    handles = {"YouTube": "@TokenWaster", "X": "@tokenwaster",
               "TikTok": "@tokenwaster", "Instagram": "@tokenwaster",
               "GitHub": "the harness itself, open"}
    socials = [{"name": n, "url": u, "colour": c, "path": p,
                "handle": handles.get(n, "")}
               for n, u, c, p in SOCIALS]
    td = {tid: info for tid, info in collect_task_data(runs).items()
          if tid in tdefs}
    models = {m for info in td.values() for m in info["agg"]}
    return _compiled(LINKS_TEMPLATE).render(
        css=BASE_CSS, nav=_nav(""), brand=_brand(""), brand_svg=BRAND_SVG,
        socials=socials, n_models=len(models), n_tasks=len(tdefs),
        n_runs=len(runs), suite_version=config.suite_version())


def build_special_page(dataset_label: str = "") -> str:
    from . import thinking
    d = special_summary()
    prev = None
    for r in d["rows"]:
        r["show_model"] = (r["model"] != prev)
        prev = r["model"]
    turns = special_turns_summary()
    budget = special_budget_summary()
    th_rows = [dict(r, verdict=thinking.verdict(r)) for r in thinking.results()]
    th_cost = thinking.cost_rollup()
    th_support = thinking.load_support()
    return _compiled(SPECIAL_STATIC_TEMPLATE).render(
        nav=_nav(""), brand=_brand(""), css=BASE_CSS, dataset_label=dataset_label,
        turns=turns, budget=budget, th_rows=th_rows, th_cost=th_cost,
        th_support=sorted(
            ({"model": k, **v} for k, v in th_support.items()),
            key=lambda s: (s.get("verdict") != "honoured", s["model"])),
        th_candidates=thinking.CANDIDATES,
        any_output=bool(d["rows"] or turns.get("rows") or budget.get("rows")
                        or th_rows),
        **d)


def build_compare_page(runs: list[dict], tdefs: dict, dataset_label: str = "",
                       dataset_key: str = "live") -> str:
    import json as _json

    _, hidden = _model_prefs()
    task_data = {tid: info for tid, info in collect_task_data(runs).items()
                 if tid in tdefs}
    by_model: dict[str, list] = {}
    for tid, info in task_data.items():
        for m, e in info["agg"].items():
            if m not in hidden:
                by_model.setdefault(m, []).append(e)
    _full = covered_models(task_data)
    by_model = {m: rs for m, rs in by_model.items() if m in _full}
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

    payload = {"models": ranked, "names": sorted(ranked, key=str.lower),
               "data": data, "cats": cat_list}
    data_json = _json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    return _compiled(COMPARE_TEMPLATE).render(
        cost_note=cost_note(),
        nav=_nav(""), brand=_brand(""), css=BASE_CSS, data_json=data_json,
        dataset_label=dataset_label, dataset_key=dataset_key)


_GEN_LOCK = threading.RLock()

_STAMP_NAME = ".render-stamp.json"


def _render_fingerprint(runs_dir: Path) -> str:
    """Everything a rendered page can depend on, cheap to compute: file
    (mtime, size) over the data trees plus the rendering code itself."""
    import hashlib
    import os
    h = hashlib.sha256()

    def tree(base: Path, suffixes=(".json", ".yaml")):
        if not base.is_dir():
            return
        for root, _dirs, files in os.walk(base):
            for f in files:
                if suffixes and not f.endswith(suffixes):
                    continue
                fp = os.path.join(root, f)
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                h.update(f"{fp}|{st.st_mtime_ns}|{st.st_size};".encode())

    tree(runs_dir)
    tree(config.TASKS_DIR, suffixes=())
    tree(config.MODELS_DIR)
    tree(getattr(config, "SPECIAL_DIR", Path("_none")))
    for f in (config.ROOT / "directives.yaml", config.ROOT / "families.yaml",
              config.ROOT / "SUITE_VERSION",
              getattr(config, "PRIVATE_DIR", Path("_none")) / "mirror.json"):
        try:
            st = f.stat()
            h.update(f"{f}|{st.st_mtime_ns}|{st.st_size};".encode())
        except OSError:
            pass
    code = Path(__file__).parent
    for mod in ("report.py", "assess.py", "apicost.py", "fit.py", "mirror.py",
                "budget.py", "thinking.py", "registry.py", "tasks.py"):
        try:
            st = (code / mod).stat()
            h.update(f"{mod}|{st.st_mtime_ns}|{st.st_size};".encode())
        except OSError:
            pass
    return h.hexdigest()


def _one_render_at_a_time(fn):
    """Serialise renders, and skip one entirely when nothing it reads has
    changed since the stamp was written (default live render only — exports
    and archive renders pass explicit dirs and always run)."""
    import functools
    import json as _json

    @functools.wraps(fn)
    def inner(runs_dir=None, out_dir=None, dataset_label="",
              dataset_key="live", tasks_dir=None, public_nav=False):
        with _GEN_LOCK:
            default_live = (runs_dir is None and out_dir is None
                            and tasks_dir is None and dataset_key == "live"
                            and not public_nav)
            if default_live:
                stamp = config.REPORTS_DIR / _STAMP_NAME
                fp = _render_fingerprint(config.RUNS_DIR)
                try:
                    if (stamp.read_text(encoding="utf-8").strip() == fp
                            and (config.REPORTS_DIR / "index.html").is_file()):
                        return config.REPORTS_DIR
                except OSError:
                    pass
            out = fn(runs_dir, out_dir, dataset_label, dataset_key,
                     tasks_dir, public_nav)
            if default_live:
                try:
                    stamp.write_text(_render_fingerprint(config.RUNS_DIR),
                                     encoding="utf-8")
                except OSError:
                    pass
            return out
    return inner


@_one_render_at_a_time
def generate_all(runs_dir: Path | None = None, out_dir: Path | None = None,
                 dataset_label: str = "", dataset_key: str = "live",
                 tasks_dir: Path | None = None, public_nav: bool = False) -> Path:
    global _RUNS_BASE, _PUBLIC_NAV, _DATASET_KEY
    runs_dir = runs_dir or config.RUNS_DIR
    out_dir = out_dir or config.REPORTS_DIR
    prev_base, prev_public = _RUNS_BASE, _PUBLIC_NAV
    prev_key = _DATASET_KEY
    _RUNS_BASE = runs_dir
    _PUBLIC_NAV = public_nav
    _DATASET_KEY = dataset_key
    global _COST_NOTE, _EQUIV_MODELS, _REGISTRY_CACHE, _GEN_CACHE
    _COST_NOTE = None
    _EQUIV_MODELS = None
    _REGISTRY_CACHE = None
    prev_gen = _GEN_CACHE
    _GEN_CACHE = {} if prev_gen is None else prev_gen
    from . import apicost as _ac0
    _ac0.reset_caches()
    try:
        runs = load_all_runs(runs_dir)
        tdefs = _task_defs(tasks_dir)
        from .util import strip_output_comments
        def _w(path, html):
            if "</body>" in html and 'class="srail"' not in html:
                html = html.replace("</body>", _social_rail() + "</body>", 1)
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
        _dstats = discrimination_stats(runs, tdefs)
        for tid, info in _tdata.items():
            if tid not in tdefs:
                continue
            _w(out_tasks / f"{tid}.html",
               build_task_report(tid, info, tdefs.get(tid), _acfg, _suspect,
                                 _dstats))
        out_models = out_dir / "models"
        out_models.mkdir(parents=True, exist_ok=True)
        for stale in out_models.glob("*.html"):
            stale.unlink()
        _, hidden = _model_prefs()
        seen_models = sorted({res["model"] for r in runs
                              for res in r["results"]} - hidden)
        versions = load_versions() if dataset_key == "live" else None
        mirror_by_model: dict[str, dict] = {}
        if dataset_key == "live":
            try:
                from .mirror import contamination_delta
                mirror_by_model = {r["model"]: r
                                   for r in contamination_delta(_tdata)}
            except Exception:
                mirror_by_model = {}
        confirmed: dict[str, dict] = {}
        if dataset_key == "live":
            try:
                from .lmstudio import confirm_sampling
                confirmed = confirm_sampling(runs_dir)
            except Exception:
                confirmed = {}
        for m in seen_models:
            _w(out_models / f"{_slug_name(m)}.html",
               build_model_report(m, runs, tdefs, dataset_label, versions,
                                  _mirror_detail_row(mirror_by_model.get(m)),
                                  _confirmed_row(confirmed.get(m)), _dstats))
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
            _w(out_dir / "special.html", build_special_page(dataset_label))
            _w(out_dir / "links.html", build_links_page(runs, tdefs))
        index = out_dir / "index.html"
        _w(index, build_index(runs, tasks_dir=tasks_dir,
                              dataset_label=dataset_label, dataset_key=dataset_key,
                              versions=versions))
        return index
    finally:
        _RUNS_BASE = prev_base
        _PUBLIC_NAV = prev_public
        _DATASET_KEY = prev_key
        _GEN_CACHE = prev_gen
