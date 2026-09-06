
import html as _html
import threading
import colorsys
import html
import re
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, BaseLoader

from . import config
from .security import isolated_preview
from .experience import model_name
from .util import read_json, read_jsonl

def _asset(name: str) -> str:
    return (Path(__file__).with_name("presentation") / name).read_text(encoding="utf-8")


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
    ("Overview", "index.html", False), ("Find a model", "choose.html", False), ("Stories", "stories.html", False), ("Families", "family.html", False),
    ("Task difficulty", "discriminate.html", False),
    ("Compare", "compare.html", False),
    ("Run", "/run", True), ("Watch", "/watch", True),
    ("Review", "/review", True),
    ("Backend", "/backend", True), ("Manage data", "/manage", True),
    ("Organize", "/families-edit", True),
    ("Mirror", "/mirror", True),
    ("Experiments", "special.html", False),
    ("Methodology", "info.html", False),
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
        if label == "Experiments" and not _PUBLIC_NAV:
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
    return f"{round(n):,}"


def last_response_text(run_id: str, model: str, task: str, limit: int = 5000) -> str:
    events = read_jsonl(_RUNS_BASE / run_id / model / task / "transcript.jsonl")
    text = ""
    for ev in events:
        if ev.get("event") == "response" and ev.get("text"):
            text = ev["text"]
    if len(text) > limit:
        text = text[:limit] + f"\n…[truncated, {len(text) - limit} more chars in transcript]"
    return text


def _receipt_url(run_id: str, model: str, task: str = "") -> str:
    parts = [quote(run_id), quote(model)] + ([quote(task)] if task else [])
    if _PUBLIC_NAV:
        try:
            base = _RUNS_BASE.relative_to(config.ROOT).as_posix()
        except ValueError:
            base = "runs"
        return ("https://github.com/tokenwaster/llm-testing-public/tree/main/"
                + "/".join([base, *parts]))
    return "/data/" + "/".join(parts) + "/"


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
            f'{html.escape(model_name(name))}</a>')


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


_SCATTER_HOVER_JS = _asset("scatter_hover_js.html")


def bar(value: float, vmax: float, width=140) -> str:
    w = 0 if vmax <= 0 else max(2, value / vmax * width)
    return (f'<span class="track" style="width:{width}px">'
            f'<span class="fill" style="width:{w:.0f}px"></span></span>')



BASE_CSS = _asset("base_css.css")

HEADER_CSS = _asset("header_css.css")

BASE_CSS = BASE_CSS.replace("__HEADER_CSS__", HEADER_CSS)

BASE_CSS = BASE_CSS.replace(
    "--s8:#d95926;", "--s8:#d95926;" + _EXTRA_DARK).replace(
    "--s8:#eb6834;", "--s8:#eb6834;" + _EXTRA_LIGHT)

_MATRIX_CSS = _asset("matrix_css.css")
BASE_CSS += _MATRIX_CSS

RUN_TEMPLATE = _asset("run.html")

TASK_TEMPLATE = _asset("task.html")

INDEX_TEMPLATE = _asset("index.html")

_env = Environment(loader=BaseLoader(), autoescape=False)
_TPL_CACHE: dict = {}


def _compiled(src: str):
    t = _TPL_CACHE.get(src)
    if t is None:
        t = _TPL_CACHE[src] = _env.from_string(src)
    return t

_FOCUS_JS = _asset("focus_js.html")

_VERSCMP_JS = _asset("verscmp_js.html")

_SORT_JS = _asset("sort_js.html")




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
    return ('<b>Cost depends on how the model was accessed.</b> API figures use '
            'provider billing or list prices on recorded usage. CLI subscriptions '
            'have no per-token price: their cost is shown as — and excluded from '
            'price comparisons. Local energy estimates, when available, exclude '
            'hardware purchase costs. Missing prices are not free. '
            f'<a href="{up}info.html#costbasis">Cost methodology</a>.')



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
    if mo:
        return mo.is_cli
    name = str(rs[0].get("model") or "") if rs else ""
    return name.startswith(("claude-cli-", "codex-cli-"))


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
    prices = [r.get("cost_usd") for r in rs]
    cost = sum(prices) if prices and all(p is not None for p in prices) else None
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
            "cost": fmt_cost(None if _is_subscription([e]) else e.get("cost_usd")),
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
        "cost": fmt_cost(None if _is_subscription([e]) else e.get("cost_usd")),
    } for e in reversed(info["history"])]

    def _stage(entry, label):
        row = next(r for r in rows if r["model"] == entry["model"])
        app = (_RUNS_BASE / entry["run_id"] / entry["model"] / task_id
               / "workspace" / "app.html")
        srcdoc = ""
        if tdef and tdef.scoring_type == "webapp" and app.is_file():
            srcdoc = html.escape(isolated_preview(app.read_text(encoding="utf-8", errors="replace")),
                                 quote=True)
        return {"label": label, "model": entry["model"], "chip": row["chip"],
                "why": row["why_full"] or row["summary"], "srcdoc": srcdoc,
                "output": row["output"],
                "files": row["files"] if _RUNS_BASE == config.RUNS_DIR else ""}

    evidence = []
    if results:
        evidence.append(_stage(results[0], "Best recorded build" if tdef and
                               tdef.scoring_type == "webapp" else
                               "Best recorded answer"))
    failures = [e for e in results if e["score"].get("status") == "scored"
                and (e["score"].get("score") or 0) < pass_thresh]
    if failures:
        evidence.append(_stage(min(failures,
                                   key=lambda e: e["score"].get("score") or 0),
                               "Representative failure"))

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
        tiles=tiles, rows=rows, history=history, evidence=evidence)


def build_run_report(run: dict, tdefs: dict | None = None) -> str:
    tdefs = tdefs if tdefs is not None else _task_defs()
    models = [m for m in run["manifest"]["models"]
              if any(r["model"] == m for r in run["results"])]
    summaries = [{**_model_summary(run, m), "model_link": _mlink(m, "../")}
                 for m in models]

    total_tokens = sum(s["tokens_total"] for s in summaries)
    prices = [r.get("cost_usd") for r in run["results"] if not _is_subscription([r])]
    total_cost = sum(prices) if prices and all(p is not None for p in prices) else None
    pending = sum(s["pending"] for s in summaries)
    scored_avg = _avg([s["avg_score_val"] for s in summaries])
    tiles = [
        {"v": f"{scored_avg:.3f}" if scored_avg is not None else "—", "k": "avg score"},
        {"v": str(len(models)), "k": "models"},
        {"v": str(len(run["manifest"]["tasks"])), "k": "tasks"},
        {"v": fmt_ms(sum(r["wall_ms"] for r in run["results"])), "k": "total wall"},
        {"v": f"{total_tokens:,}", "k": "tokens"},
        {"v": fmt_cost(total_cost), "k": "recorded non-subscription cost"},
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
                if r.get("cost_usd") and not _is_subscription([r]):
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


MODEL_TEMPLATE = _asset("model.html")


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
    if (summary or {}).get("cost_basis") == "subscription":
        from . import apicost as _ac
        _oh = _ac.cli_overhead_for(mo) if mo else None
        _sc = int((summary or {}).get("scaffold_tokens") or 0)
        add("Cost",
            "<b>not reported</b> &mdash; subscription"
            '<div class="note" style="font-size:11.5px;margin-top:2px">'
            "Measured through a subscription CLI: there is no per-token price, "
            "so any figure here would be invented. This model is also left out "
            "of the value and cost-per-point views."
            + (f" For scale, the CLI sent <b>{int(_oh):,}</b> input tokens of "
               f"its own instructions and tools per request "
               f"({_sc:,} across this model's cells) &mdash; but that is not a "
               f"deduction you can make, because the CLI is a different agent "
               f"doing more work, not a wrapper." if _oh else "")
            + " Cost arrives when the full suite has been run through the API. "
            "<a href=\"../info.html#costbasis\">Why, and what we measured</a>."
            "</div>")
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
        {"v": f"{npass}/{len(graded)}", "k": "tasks ≥ 0.80"},
        {"v": s["att_per_pass"], "k": "tries / pass (lower=better)"},
        {"v": s["tps"], "k": "gen tok/s"},
        {"v": s["cost"], "k": "cost / run"},
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
        avg = _avg(sc)
        cats.append({"name": cat, "chip": _score_cell(avg), "score": avg})

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

    ranked_cats = sorted((c for c in cats if c["score"] is not None),
                         key=lambda c: c["score"], reverse=True)
    strongest = ranked_cats[0] if ranked_cats else None
    weakest = ranked_cats[-1] if ranked_cats else None
    top_cats = ([c for c in ranked_cats
                 if strongest and abs(c["score"] - strongest["score"]) < 0.0005]
                if ranked_cats else [])
    frontier_ids = set((dstats or {}).get("frontier_subset") or [])
    frontier_vals = [e["score"]["score"] for tid, e in mine
                     if tid in frontier_ids and e["score"].get("status") == "scored"]
    low = min(((e["score"]["score"], tid) for tid, e in mine
               if e["score"].get("status") == "scored"), default=(None, ""))
    verdict = {
        "title": ((f"Perfect in {len(top_cats)} categories; pressure point: "
                   f"{weakest['name']}")
                  if strongest and strongest["score"] >= 0.999 and len(top_cats) > 1
                  else f"Strongest in {strongest['name']}; pressure point: {weakest['name']}"
                  if strongest and weakest and strongest != weakest else
                  "A complete measured profile"),
        "body": (f"{npass} of {len(graded)} graded tasks clear the pass line. "
                 + (f"On the frontier it clears {sum(v >= 0.8 for v in frontier_vals)} "
                    f"of {len(frontier_vals)} measured task(s). " if frontier_vals else "")
                 + (f"Its lowest result is {low[0]:.3f} on {low[1]}."
                    if low[0] is not None else "No scored task is available.")),
        "facts": [
            {"v": attr_disp, "k": "attributed score"},
            {"v": s["first_try"], "k": "first-try clean"},
            {"v": fmt_span(s["wall_ms_sum"]), "k": "total measured time"},
            {"v": (f"{sum(v >= 0.8 for v in frontier_vals)}/{len(frontier_vals)}"
                   if frontier_vals else "—"), "k": "frontier record"},
        ],
    }
    verdict_tape = []
    for tid, e in sorted(mine):
        cell = _mx_cell(e, tdefs[tid], acfg, suspect,
                        f"../tasks/{tid}.html#m-{_slug_name(model)}")
        verdict_tape.append({"id": tid, "href": cell["href"],
                             "cls": cell["cls"], "a": cell.get("a", "0"),
                             "tip": cell["tip"]})

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
        css=BASE_CSS, model=html.escape(model_name(model)), slug_q=quote(model),
        where=where, dataset_label=dataset_label, n_runs=len(my_runs),
        tiles=tiles, cats=cats, task_rows=task_rows, run_rows=run_rows,
        runmatrix=runmatrix,
        detail_rows=detail_rows, model_links=model_links, asmt=asmt,
        verdict=verdict, verdict_tape=verdict_tape)


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
    import json as _json

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

    evidence: dict[str, dict] = {}

    def _mcell(entry, tdef, model=None):
        href = f"tasks/{tdef.id}.html" + (f"#m-{_slug_name(model)}" if model else "")
        cell = _mx_cell(entry, tdef, _acfg, _suspect, href)
        if entry is None or model is None:
            return cell
        dx = diagnose(entry, tdef, _acfg, _suspect) or {}
        eid = str(len(evidence))
        score = entry.get("score") or {}
        value = score.get("score")
        served = entry.get("served_by") or []
        sampling = entry.get("sampling_used") or {}
        evidence[eid] = {
            "model": model,
            "task": tdef.id,
            "score": "—" if value is None else f"{value:.3f}",
            "classification": dx.get("category") or entry.get("status") or "unknown",
            "reason": dx.get("detail") or score.get("summary") or "No detail recorded.",
            "attempts": entry.get("n_attempts") or len(entry.get("attempts") or []),
            "runs": entry.get("n_scored") or entry.get("n_runs") or 1,
            "run": entry.get("run_id") or "—",
            "provider": ", ".join(str(x) for x in served) or "not recorded",
            "sampling": (", ".join(f"{k}={v}" for k, v in sorted(sampling.items()))
                         or "provider default / not settable"),
            "effort": entry.get("effort_used") or "not recorded",
            "hash": entry.get("task_hash") or "not recorded",
            "task_url": href,
            "files": _receipt_url(entry.get("run_id") or "", model, tdef.id),
        }
        cell["ev"] = eid
        return cell

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
            tied = (_rk != 1 and _lead_v is not None and abs(agg - _lead_v) < 1e-9)
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

    finding = {
        "title": ("Small gaps at the top"
                  if _dstats["top_spread"] <= 0.05 else
                  "Where the leading models separate"),
        "body": (f"The top {_dstats['cohort_k']} models span only "
                 f"{_dstats['top_spread']:.2f} in mean score. "
                 f"{_dstats['n_frontier']} frontier task(s) still beat the top "
                 f"cohort; {_dstats['n_ceiling']} are already ceiling tasks."),
    } if _dstats.get("rows") else None
    _tone = {"frontier": "frontier", "discriminator": "hard",
             "floor-gate": "hard", "ceiling": "easy", "dead": "easy"}
    finding_tape = [{"id": r["tid"], "flag": r["flag"],
                     "cls": _tone.get(r["flag"], "mid")}
                    for r in sorted(_dstats.get("rows") or [],
                                    key=lambda x: x["tid"])]

    lab_notes = []
    recent_runs = runs[-8:]
    recent_run_ids = {run["run_id"] for run in recent_runs}
    recent_models = {res["model"] for run in recent_runs for res in run["results"]}
    repeat_candidates = []
    for tid, info in task_data.items():
        histories: dict[str, list[dict]] = {}
        current_hash = getattr(tdefs[tid], "content_hash", "")
        for entry in info["history"]:
            score = entry.get("score") or {}
            if (score.get("status") == "scored"
                    and score.get("score") is not None
                    and entry.get("run_id") in recent_run_ids
                    and (not current_hash or entry.get("task_hash") == current_hash)):
                histories.setdefault(entry["model"], []).append(entry)
        for model, entries in histories.items():
            if len(entries) < 3:
                continue
            values = [e["score"]["score"] for e in entries]
            repeat_candidates.append((max(values) - min(values), model, tid, values,
                                      entries[-1].get("task_hash") or "not recorded"))
    if repeat_candidates:
        spread, model, tid, values, task_hash = max(repeat_candidates)
        shown = " → ".join(f"{v:.3f}" for v in values[-5:])
        lab_notes.append({
            "kind": "Repeatability",
            "title": f"Same task. A {spread:.3f} swing.",
            "body": (f"{model} answered {tid} {len(values)} times under the "
                     "current task hash. The score did not settle on one result."),
            "receipt": f"{shown} · task {tid}",
            "caveat": f"n={len(values)} · task hash {task_hash} · every scored run remains in the mean.",
            "href": f"tasks/{tid}.html#m-{_slug_name(model)}",
        })

    shape_candidates = []
    for model in recent_models:
        if _cover.get(model, 0) < _n_suite:
            continue
        cat_values: dict[str, list[float]] = {}
        for entry in by_model.get(model, []):
            score = entry.get("score") or {}
            if score.get("status") == "scored" and score.get("score") is not None:
                cat_values.setdefault(entry["category"], []).append(score["score"])
        means = [(sum(values) / len(values), cat) for cat, values in cat_values.items()]
        if len(means) >= 3:
            best, worst = max(means), min(means)
            shape_candidates.append((best[0] - worst[0], model, best, worst))
    if shape_candidates:
        gap, model, best, worst = max(shape_candidates)
        best_name, worst_name = best[1].replace("-", " "), worst[1].replace("-", " ")
        lab_notes.append({
            "kind": "Capability shape",
            "title": f"{model} is not one score.",
            "body": (f"Its strongest measured category is {best_name} at {best[0]:.3f}; "
                     f"its pressure point is {worst_name} at {worst[0]:.3f}."),
            "receipt": f"{best_name} {best[0]:.3f} · {worst_name} {worst[0]:.3f} · gap {gap:.3f}",
            "caveat": "Category means describe this suite's measured tasks, not every possible use.",
            "href": f"models/{_slug_name(model)}.html",
        })

    family_members: dict[str, list[tuple[str, float, bool]]] = {}
    for model in all_models:
        family = fam_of.get(model)
        score = summaries[model].get("avg_score_val")
        if family and score is not None and _cover.get(model, 0) >= _n_suite:
            family_members.setdefault(family, []).append(
                (model, score, summaries[model]["local"]))
    local_candidates = []
    for family, members in family_members.items():
        locals_ = [m for m in members if m[2]]
        hosted = [m for m in members if not m[2]]
        if locals_ and hosted:
            best_local = max(locals_, key=lambda m: m[1])
            best_hosted = max(hosted, key=lambda m: m[1])
            local_candidates.append((best_hosted[1] - best_local[1], family,
                                     best_hosted, best_local))
    if local_candidates:
        gap, family, hosted, local = max(local_candidates)
        lab_notes.append({
            "kind": "Local tradeoff",
            "title": f"The {family} local gap is {gap:.3f}.",
            "body": (f"{hosted[0]} leads the hosted side at {hosted[1]:.3f}. "
                     f"{local[0]} is the strongest fully measured local member at {local[1]:.3f}."),
            "receipt": f"hosted {hosted[1]:.3f} · local {local[1]:.3f} · gap {gap:.3f}",
            "caveat": "Capability is only half the decision; the Families page adds VRAM and speed.",
            "href": f"family.html?family={quote(family)}",
        })
    if dataset_key != "live":
        lab_notes = []

    first_run: dict[str, str] = {}
    for r in runs:
        for m in {x["model"] for x in r["results"]}:
            first_run.setdefault(m, r["run_id"])
    activity = []
    seen_activity: set[str] = set()
    for r in reversed(runs):
        models = sorted({x["model"] for x in r["results"]})
        if not models:
            continue
        new = [m for m in models if first_run.get(m) == r["run_id"]]
        candidates = new or [m for m in models if m not in seen_activity]
        if not candidates:
            continue
        focus = candidates[0]
        seen_activity.add(focus)
        stopped = r["manifest"].get("stopped_reason")
        kind = "new model" if focus in new else "measured run"
        title = (focus + " entered the benchmark" if focus in new
                 else focus + " was measured")
        activity.append({"kind": "paused" if stopped else kind,
                         "title": title, "run": r["run_id"],
                         "meta": (f"{len(r['results'])} result(s) · "
                                  + (f"stopped: {stopped}" if stopped else
                                     r["run_id"].split("_")[0]))})
        if len(activity) == 4:
            break

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
        finding=finding, finding_tape=finding_tape, lab_notes=lab_notes,
        activity=activity,
        evidence_json=_json.dumps(evidence, separators=(",", ":")).replace("</", "<\\/"),
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

INFO_TEMPLATE = _asset("info.html")


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
            "tid": tid, "tier": t.tier,
            "lane": getattr(t, "scoring_type", "unknown"),
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


DISCRIMINATE_TEMPLATE = _asset("discriminate.html")


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
    ent: dict[str, list[tuple[str, dict]]] = {}
    for tid, info in td.items():
        for m, e in info["agg"].items():
            if m not in hidden and e["score"].get("status") == "scored":
                ent.setdefault(m, []).append((tid, e))

    _fp: dict[str, dict | None] = {}
    fams: dict[str, list[dict]] = {}
    for m, cells in ent.items():
        es = [e for _tid, e in cells]
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
        cat_values: dict[str, list[float]] = {}
        for tid, e in cells:
            cat_values.setdefault(tdefs[tid].category, []).append(
                e["score"]["score"])
        sigmas = [e["score_sigma"] for e in es
                  if e.get("n_scored", 1) > 1
                  and e.get("score_sigma") is not None]
        fams.setdefault(fam, []).append({
            "model": m, "score": sum(e["score"]["score"] for e in es) / len(es),
            "n": len(es), "coverage": len(es) / n_suite, "local": local,
            "weights_gb": weights, "vram_ref_gb": vram_ref,
            "native_ctx": (fp or {}).get("native_ctx"),
            "quant": (fp or {}).get("quant"),
            "tps": (sum(tps_vals) / len(tps_vals)) if tps_vals else None,
            "categories": {c: sum(v) / len(v) for c, v in cat_values.items()},
            "trials": sum(e.get("n_scored", 1) for e in es),
            "repeat_cells": sum(e.get("n_scored", 1) > 1 for e in es),
            "stability": (sum(sigmas) / len(sigmas)) if sigmas else None,
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


FAMILY_TEMPLATE = _asset("family.html")


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
            "raw": mm["model"],
            "model": _mlink(mm["model"]),
            "where": "local ⚡" if mm["local"] else "hosted",
            "kind": "local" if mm["local"] else "hosted",
            "local": mm["local"],
            "score_num": mm["score"],
            "score": f"{mm['score']:.3f}", "score_v": f"{mm['score']:.4f}",
            "bar": bar(mm["score"], 1.0, width=90),
            "size": size, "size_v": size_v,
            "vram_num": mm.get("vram_ref_gb"),
            "tps": (f"{mm['tps']:.0f}" if mm["tps"] else "—"),
            "tps_v": f"{mm['tps'] or 0:.1f}",
            "cov": ("" if mm["coverage"] >= 0.999 else " partial"),
            "trials": mm.get("trials", mm.get("n", 1)),
            "repeat_cells": mm.get("repeat_cells", 0),
            "stability": mm.get("stability"),
            "stability_disp": (f"±{mm['stability']:.3f}"
                               if mm.get("stability") is not None else "—"),
            "stability_v": (f"{mm['stability']:.6f}"
                            if mm.get("stability") is not None else ""),
        }

    def _full(v):
        return [x for x in v if x.get("coverage", 0) >= 0.999] or []

    grouped = {f: v for f, v in fams.items() if v}
    fam_cards = []

    def _card_key(f):
        got = _full(grouped[f])
        return -max((x["score"] for x in got), default=-1)

    for f in sorted(grouped, key=_card_key):
        members = grouped[f]
        has_local = any(x["local"] for x in members)
        has_hosted = any(not x["local"] for x in members)
        has_both = has_local and has_hosted
        got = _full(members)
        if not got:
            continue
        ranked = got
        rows = [fmt(x) for x in members]
        leader = max(ranked, key=lambda x: x["score"])
        local_members = [x for x in ranked if x["local"]]
        best_local = max(local_members, key=lambda x: x["score"]) if local_members else None
        fastest = max((x for x in members if x.get("tps")),
                      key=lambda x: x["tps"], default=None)
        cat_values: dict[str, list[float]] = {}
        for member in ranked:
            for cat, score in member.get("categories", {}).items():
                cat_values.setdefault(cat, []).append(score)
        cats = [{"name": cat, "score": sum(values) / len(values)}
                for cat, values in sorted(cat_values.items())]
        for cat in cats:
            cat["score_v"] = f"{cat['score']:.4f}"
            cat["score"] = f"{cat['score']:.2f}"
        app_values = cat_values.get("one-shot-apps") or []
        min_vram = min((x["vram_ref_gb"] for x in local_members
                        if x.get("vram_ref_gb")), default=0)
        stability_values = [x["stability"] for x in members
                            if x.get("stability") is not None]
        if has_both and best_local:
            verdict = (f"{leader['model']} leads at {leader['score']:.3f}. "
                       f"The best local option, {best_local['model']}, trails by "
                       f"{leader['score'] - best_local['score']:.3f}.")
        elif len(ranked) > 1:
            verdict = (f"{leader['model']} leads at {leader['score']:.3f}; the "
                       f"family spans {max(x['score'] for x in ranked) - min(x['score'] for x in ranked):.3f}.")
        else:
            verdict = (f"{leader['model']} is the only measured member, at "
                       f"{leader['score']:.3f}. Treat this as a baseline, not a ladder.")
        fam_cards.append({
            "name": f, "n": len(members),
            "span": ((f"{ranked[0]['score']:.3f}" if len(ranked) == 1 else
                      f"{min(x['score'] for x in ranked):.3f}–"
                      f"{max(x['score'] for x in ranked):.3f}")),
            "both": has_both, "has_local": has_local,
            "kind": "mixed" if has_both else "local" if has_local else "hosted",
            "rows": rows, "cats": cats,
            "model_names": " ".join(x["model"] for x in members),
            "min_vram": f"{min_vram:.2f}" if min_vram else "0",
            "best_v": f"{leader['score']:.6f}",
            "apps_v": f"{sum(app_values) / len(app_values):.6f}" if app_values else "-1",
            "speed_v": f"{fastest['tps']:.6f}" if fastest else "-1",
            "stability_v": (f"{1 - sum(stability_values) / len(stability_values):.6f}"
                            if stability_values else "-1"),
            "verdict": verdict,
            "facts": [
                {"v": leader["model"], "k": "leader"},
                {"v": (best_local["model"] if best_local else
                       f"{len(members)} measured"), "k": "best local" if best_local else "members"},
                {"v": (f"{fastest['tps']:.0f} tok/s" if fastest else "—"), "k": "fastest pace"},
                {"v": (f"{sum(x.get('trials', x.get('n', 1)) for x in members)} / "
                       f"{sum(x.get('repeat_cells', 0) for x in members)}"),
                 "k": "trials / repeated cells"},
            ],
            "members": [{"name": x["model"], "score": x["score"]} for x in members],
            "cats_json": [{"name": cat, "score": sum(values) / len(values)}
                          for cat, values in sorted(cat_values.items())],
            "change": "No like-for-like version change is available yet.",
        })

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
                a, b = p["versions"][-2:]
                latest = p["pairs"].get(f"{a}|{b}")
                overall = (latest or {}).get("overall") or {}
                delta = overall.get("delta")
                if delta is not None:
                    direction = "+" if delta > 0 else ""
                    for card in fam_cards:
                        if card["name"] == fam:
                            card["change"] = (f"v{a} → v{b}: {direction}{delta:.3f} "
                                              f"across {overall.get('n_tasks', 0)} "
                                              "like-for-like task scores.")
        if blob:
            import json as _json
            verscmp = _json.dumps({k: blob[k] for k in sorted(blob)}
                                  ).replace("</", "<\\/")
    import json as _json
    family_json = _json.dumps([
        {"name": f["name"], "verdict": f["verdict"], "facts": f["facts"],
         "members": f["members"], "cats": f["cats_json"], "change": f["change"]}
        for f in fam_cards], separators=(",", ":")).replace("</", "<\\/")
    return _compiled(FAMILY_TEMPLATE).render(
        nav=_nav(""), brand=_brand(""),
        sort_js=_SORT_JS, scatter_js=_SCATTER_HOVER_JS,
        verscmp=verscmp, verscmp_js=_VERSCMP_JS,
        css=BASE_CSS, fam_cards=fam_cards, family_json=family_json,
        size_chart=size_chart,
        dataset_label=dataset_label, dataset_key=dataset_key,
        suite_version=config.suite_version())


COMPARE_TEMPLATE = _asset("compare.html")


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


SPECIAL_STATIC_TEMPLATE = _asset("special_static.html")


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


LINKS_TEMPLATE = _asset("links.html")


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
            "costVal": round(s["cost_val"], 6) if s.get("cost_val") is not None else None,
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
    tiers = task_tiers(runs, tdefs)

    from .experience import paired_inputs
    from .security import json_for_script
    payload = {"models": ranked, "names": sorted(ranked, key=str.lower),
               "data": data, "cats": cat_list, "tiers": tiers,
               "evidence": paired_inputs(runs, tdefs)}
    data_json = json_for_script(payload)
    return _compiled(COMPARE_TEMPLATE).render(
        shared_js=_asset("experience.js"),
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
    tree(Path(__file__).with_name("presentation"), suffixes=())
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
    for mod in ("report.py", "util.py", "experience.py", "security.py", "assess.py", "apicost.py", "fit.py", "mirror.py",
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
            from .experience import sharing_footer
            from .security import secure_report
            prefix = "../" * len(path.relative_to(out_dir).parts[:-1])
            version = runs[-1]["manifest"].get("suite_version", config.suite_version()) if runs else config.suite_version()
            asof = max((r["manifest"].get("finished") or r["manifest"].get("started") or "" for r in runs), default="")
            html = sharing_footer(html, version, asof, prefix)
            path.write_text(secure_report(strip_output_comments(html)), encoding="utf-8")
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
        from .experience import write_experience
        write_experience(out_dir, runs, tdefs, dataset_key, dataset_label, _w)
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
