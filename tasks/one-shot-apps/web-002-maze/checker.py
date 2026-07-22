"""web-002 v2 checker: bots must EXPLORE (discover the exit, backtrack,
remember dead ends) — omniscient shortest-path walkers fail here."""
import os
from collections import deque
from pathlib import Path

import pytest

APP = Path(__file__).parent / "app.html"

for _parent in Path(__file__).resolve().parents:
    _pw = _parent / ".pw-browsers"
    if _pw.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_pw)
        break


def _launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        return p.chromium.launch(channel="chromium")


@pytest.fixture(scope="module")
def page():
    assert APP.exists(), "app.html missing"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = _launch(p)
        pg = browser.new_page()
        pg.goto(APP.as_uri())
        pg.wait_for_timeout(400)
        yield pg
        browser.close()


@pytest.fixture(scope="module")
def world(page):
    """Reset, run to completion, harvest the full state once."""
    page.evaluate("() => window.game.reset()")
    page.evaluate("() => window.game.tick(20000)")
    return page.evaluate("""() => {
        const g = window.game;
        const walls = [];
        for (let r = 0; r < g.size.rows; r++) {
            const row = [];
            for (let c = 0; c < g.size.cols; c++) row.push(g.walls(r, c));
            walls.push(row);
        }
        return {
            size: g.size, spawn: g.spawn, exit: g.exit, walls,
            elapsed: g.elapsed,
            bots: g.bots.map(b => ({path: b.path, deadEnds: b.deadEnds,
                                    finishTick: b.finishTick})),
        };
    }""")


def _shortest(world) -> int:
    """BFS shortest path length (cells entered) from spawn to exit."""
    rows, cols = world["size"]["rows"], world["size"]["cols"]
    w = world["walls"]
    start = (world["spawn"]["r"], world["spawn"]["c"])
    goal = (world["exit"]["r"], world["exit"]["c"])
    seen = {start}
    q = deque([(start, 1)])
    while q:
        (r, c), d = q.popleft()
        if (r, c) == goal:
            return d
        for dr, dc, side in ((-1, 0, "n"), (0, 1, "e"), (1, 0, "s"),
                             (0, -1, "w")):
            if not w[r][c].get(side):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    q.append(((nr, nc), d + 1))
    pytest.fail("maze has no path from spawn to exit")


def test_layout_and_size(page):
    for sel in ("#maze", "#completed", "#timer", "#reset"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#maze").bounding_box()
    assert box and box["width"] >= 380 and box["height"] >= 380, \
        "maze must render at least 400x400"


def test_api_shape(page):
    ok = page.evaluate("""() => {
        const g = window.game;
        return g && typeof g.tick === 'function'
            && typeof g.reset === 'function'
            && typeof g.walls === 'function'
            && g.size && g.spawn && g.exit
            && Array.isArray(g.bots) && g.bots.length === 24
            && g.bots.every(b => Array.isArray(b.path)
                                 && Array.isArray(b.deadEnds)
                                 && 'finishTick' in b);
    }""")
    assert ok, "window.game API incomplete (see spec)"
    size = page.evaluate("() => window.game.size")
    assert size["rows"] >= 15 and size["cols"] >= 15, "maze must be >=15x15"


def test_all_bots_finish_and_timer_freezes(page, world):
    unfinished = [i for i, b in enumerate(world["bots"])
                  if b["finishTick"] is None]
    assert not unfinished, f"bots never reached the exit: {unfinished}"
    last = max(b["finishTick"] for b in world["bots"])
    assert world["elapsed"] == last, \
        f"elapsed ({world['elapsed']}) must freeze at last arrival ({last})"
    frozen = page.evaluate("""() => {
        const before = window.game.elapsed;
        const t = document.querySelector('#timer').textContent;
        window.game.tick(50);
        return {same: window.game.elapsed === before,
                timerSame: document.querySelector('#timer').textContent === t};
    }""")
    assert frozen["same"], "game.elapsed kept advancing after all bots arrived"
    assert frozen["timerSame"], "HUD timer kept running after all bots arrived"


def test_movement_continuity(world):
    """Every step is to an adjacent cell through an open wall."""
    rows, cols = world["size"]["rows"], world["size"]["cols"]
    w = world["walls"]
    for i, b in enumerate(world["bots"]):
        path = b["path"]
        assert path, f"bot {i} has an empty path"
        assert path[0] == world["spawn"], f"bot {i} did not start at spawn"
        assert path[-1] == world["exit"], f"bot {i} path does not end at exit"
        for a, c in zip(path, path[1:]):
            dr, dc = c["r"] - a["r"], c["c"] - a["c"]
            side = {(-1, 0): "n", (0, 1): "e", (1, 0): "s", (0, -1): "w"} \
                .get((dr, dc))
            assert side, f"bot {i} teleported {a} -> {c}"
            assert not w[a["r"]][a["c"]].get(side), \
                f"bot {i} walked through a wall {a} -> {c}"


def test_bots_explore_not_omniscient(world):
    """An omniscient BFS walker walks exactly the shortest path. Explorers
    can't: average traveled path must exceed it, and most bots backtrack."""
    shortest = _shortest(world)
    lengths = [len(b["path"]) for b in world["bots"]]
    avg = sum(lengths) / len(lengths)
    assert avg > shortest * 1.15, \
        (f"average path {avg:.0f} vs shortest {shortest} — bots are walking "
         "(near-)optimal routes, which means they aren't exploring")
    backtrackers = 0
    for b in world["bots"]:
        cells = [(p["r"], p["c"]) for p in b["path"]]
        if len(set(cells)) < len(cells):
            backtrackers += 1
    assert backtrackers >= 12, \
        f"only {backtrackers}/24 bots ever backtracked — not exploration"


def test_dead_end_memory(world):
    """Tremaux bound: no PASSAGE (edge between two cells) traversed more
    than twice by the same bot — the signature of remembered dead ends.
    A forgetful walker re-walks passages 3+ times. True dead-end cells
    (single opening) additionally allow at most 2 entries."""
    rows_walls = world["walls"]
    marked_any = 0
    for i, b in enumerate(world["bots"]):
        dead = {(d["r"], d["c"]) for d in b["deadEnds"]}
        if dead:
            marked_any += 1
        edges: dict = {}
        cells: dict = {}
        prev = None
        for p in b["path"]:
            key = (p["r"], p["c"])
            cells[key] = cells.get(key, 0) + 1
            if prev is not None:
                e = tuple(sorted((prev, key)))
                edges[e] = edges.get(e, 0) + 1
            prev = key
        worst = max(edges.values(), default=0)
        assert worst <= 2, \
            (f"bot {i} walked some passage {worst} times — dead-end memory "
             "isn't preventing re-exploration (Tremaux bound is 2)")
        for cell in dead:
            r, c = cell
            openings = sum(1 for s in ("n", "e", "s", "w")
                           if not rows_walls[r][c].get(s))
            if openings == 1:
                assert cells.get(cell, 0) <= 2, \
                    (f"bot {i} entered cul-de-sac {cell} "
                     f"{cells[cell]} times — memory isn't working")
    assert marked_any >= 12, \
        f"only {marked_any}/24 bots marked any dead end — memory unused"


def test_determinism(page):
    a = page.evaluate("""() => {
        window.game.reset(42);
        window.game.tick(120);
        return window.game.bots.map(b => JSON.stringify(b.path.slice(-1)));
    }""")
    b = page.evaluate("""() => {
        window.game.reset(42);
        for (let i = 0; i < 120; i++) window.game.tick(1);
        return window.game.bots.map(b => JSON.stringify(b.path.slice(-1)));
    }""")
    assert a == b, "reset(42)+tick(120) must equal reset(42)+120x tick(1)"


def test_maze_visibly_drawn(page):
    page.evaluate("() => window.game.reset()")
    info = page.evaluate("""() => {
        const root = document.querySelector('#maze');
        const c = root && (root.tagName === 'CANVAS' ? root
                           : root.querySelector('canvas'));
        if (c) {
            const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            const colors = new Set();
            for (let i = 0; i < d.length; i += 40)
                colors.add((d[i] << 16) | (d[i+1] << 8) | d[i+2]);
            return {ok: colors.size >= 4, detail: colors.size};
        }
        const n = root ? root.querySelectorAll('*').length : 0;
        return {ok: n >= 50, detail: n};
    }""")
    assert info["ok"], f"maze not visibly drawn ({info['detail']})"


def test_runs_on_its_own(page):
    """The app must ANIMATE BY ITSELF — bots move and the timer advances over
    real time with NO external game.tick() call. A model can build a correct
    tick()/reset() API and still ship a dead maze (no autoplay loop): the
    checker's own tick() drives it to a pass while a human sees nothing move.
    Reuses the module page fixture (a nested sync_playwright would error);
    runs last, and reload()+reset() give it a clean, undriven starting state."""
    page.reload()
    page.wait_for_timeout(300)
    before = page.evaluate("() => { window.game.reset(); "
                           "return window.game.elapsed; }")
    page.wait_for_timeout(1600)
    after = page.evaluate("""() => ({
        elapsed: window.game.elapsed,
        moved: window.game.bots.filter(b => b.path.length > 1).length,
    })""")
    assert after["elapsed"] > before, (
        "the timer never advanced on its own over 1.6s — the maze only moves "
        "when something calls game.tick() externally (dead app; needs an "
        "autoplay loop)")
    assert after["moved"] > 0, (
        "no bot moved on its own over 1.6s — the app relies on the checker to "
        "drive it; it must animate by itself")
