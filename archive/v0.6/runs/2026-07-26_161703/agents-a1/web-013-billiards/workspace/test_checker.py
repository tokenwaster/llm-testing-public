"""web-013-billiards grader.

Two things are judged, both from the running game, never from source:

  * PHYSICS — the app exposes window.sim (reset/step/state, W/H/R); each law
    (motion, friction, cushions, elastic collisions, pockets, determinism) is
    its own check, driven numerically with the animation loop paused.
  * PLAYABILITY — it must be an actual game: a real mouse drag on the cue ball
    launches it (test_playable_can_shoot, the GATE), a reset control re-racks,
    and on-screen instructions say how to play.

The gate matters: if the cue ball can't be shot with the mouse, it isn't a
playable pool game, and meta.yaml caps the whole score at 0.5 no matter how
perfect the physics. Dynamic checks are folded to require motion, so a do-nothing
sim floors near zero (rule #5).
"""
import os
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
        pg = browser.new_page(viewport={"width": 1000, "height": 700})
        pg.goto(APP.as_uri())
        pg.wait_for_timeout(500)
        # stop the model's animation loop so stepping is deterministic; a missing
        # API must fail the contract test, not raise here
        try:
            pg.evaluate("() => window.sim && window.sim.pause && window.sim.pause()")
        except Exception:
            pass
        yield pg
        browser.close()


def _has_api(page) -> bool:
    return page.evaluate("""() => {
        const s = window.sim;
        return !!(s && typeof s.reset==='function' && typeof s.step==='function'
                  && typeof s.state==='function'
                  && typeof s.W==='number' && typeof s.H==='number'
                  && typeof s.R==='number');
    }""")


def _run(page, balls, dt, n):
    return page.evaluate(
        """({balls, dt, n}) => { window.sim.reset(balls);
            for (let i=0;i<n;i++) window.sim.step(dt); return window.sim.state(); }""",
        {"balls": balls, "dt": dt, "n": n})


# ------------------------------------------------------------------ physics
def test_sim_api_present(page):
    assert _has_api(page), "no window.sim API with reset/step/state/W/H/R"


def test_ball_at_rest_stays(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 200, "y": 150, "vx": 0, "vy": 0}], 1 / 120, 120)
    assert abs(s[0]["x"] - 200) < 1.0 and abs(s[0]["y"] - 150) < 1.0


def test_moves_in_travel_direction(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 100, "y": 150, "vx": 120, "vy": 0}], 1 / 240, 20)
    assert s[0]["x"] > 104


def test_friction_brings_to_rest(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 150, "y": 150, "vx": 200, "vy": 60}], 1 / 120, 1800)
    assert (s[0]["vx"] ** 2 + s[0]["vy"] ** 2) ** 0.5 < 5.0


def test_friction_is_monotonic(page):
    if not _has_api(page):
        pytest.skip("no api")
    speeds = page.evaluate(
        """({dt}) => { window.sim.reset([{x:200,y:150,vx:150,vy:40}]); const o=[];
            for(let i=0;i<40;i++){window.sim.step(dt);const b=window.sim.state()[0];
            o.push(Math.hypot(b.vx,b.vy));} return o; }""", {"dt": 1 / 120})
    assert all(speeds[i + 1] <= speeds[i] + 1e-6 for i in range(len(speeds) - 1))
    assert speeds[0] - speeds[-1] > 1.0, "speed never dropped — no friction"


def test_reflects_off_right_wall(page):
    if not _has_api(page):
        pytest.skip("no api")
    W = page.evaluate("() => window.sim.W")
    s = _run(page, [{"x": W - 60, "y": 150, "vx": 300, "vy": 0}], 1 / 240, 90)
    assert s[0]["vx"] < 0


def test_reflects_off_top_wall(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 200, "y": 40, "vx": 0, "vy": -300}], 1 / 240, 60)
    assert s[0]["vy"] > 0


def test_stays_in_bounds(page):
    if not _has_api(page):
        pytest.skip("no api")
    W = page.evaluate("() => window.sim.W")
    H = page.evaluate("() => window.sim.H")
    s = _run(page, [{"x": 300, "y": 150, "vx": 420, "vy": 260}], 1 / 240, 240)
    b = s[0]
    if b["potted"]:
        return
    assert abs(b["x"] - 300) + abs(b["y"] - 150) > 20, "ball never moved"
    assert -1 <= b["x"] <= W + 1 and -1 <= b["y"] <= H + 1


def test_head_on_transfers_momentum(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 150, "y": 150, "vx": 250, "vy": 0},
                    {"x": 205, "y": 150, "vx": 0, "vy": 0}], 1 / 480, 150)
    assert s[1]["vx"] > 40 and s[0]["vx"] < 160


def test_collision_conserves_momentum(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = _run(page, [{"x": 150, "y": 150, "vx": 240, "vy": 0},
                    {"x": 200, "y": 166, "vx": 0, "vy": 0}], 1 / 960, 200)
    assert s[1]["vx"] > 5, "no collision occurred"
    assert abs((s[0]["vx"] + s[1]["vx"]) - 240) < 40


def test_collision_does_not_create_energy(page):
    if not _has_api(page):
        pytest.skip("no api")
    s = page.evaluate(
        """() => { const dt=1/960;
            window.sim.reset([{x:150,y:150,vx:240,vy:0},{x:200,y:166,vx:0,vy:0}]);
            const ke=v=>v.reduce((s,b)=>s+b.vx*b.vx+b.vy*b.vy,0);
            const before=ke(window.sim.state());
            for(let i=0;i<200;i++) window.sim.step(dt); const st=window.sim.state();
            return {before, after: ke(st), bvx: st[1].vx}; }""")
    assert s["bvx"] > 5 and s["after"] <= s["before"] * 1.05 + 1


def test_ball_is_potted_in_corner(page):
    if not _has_api(page):
        pytest.skip("no api")
    W = page.evaluate("() => window.sim.W")
    H = page.evaluate("() => window.sim.H")
    s = _run(page, [{"x": W - 120, "y": H - 120, "vx": 300, "vy": 300}], 1 / 240, 240)
    assert s[0]["potted"] is True


def test_deterministic(page):
    if not _has_api(page):
        pytest.skip("no api")
    setup = [{"x": 180, "y": 140, "vx": 260, "vy": 120},
             {"x": 320, "y": 175, "vx": 0, "vy": 0}]
    a = _run(page, setup, 1 / 240, 120)
    b = _run(page, setup, 1 / 240, 120)
    assert a == b
    assert abs(a[0]["x"] - 180) + abs(a[0]["y"] - 140) > 10, "nothing moved"


# --------------------------------------------------------------- playability
def _cue_viewport(page):
    """Rack, then return (viewport x,y of the cue ball, canvas handle info)."""
    return page.evaluate("""() => {
        // put the cue ball at a known REST position first, so the only thing
        // that can move it is the drag under test (not leftover velocity)
        if (window.sim.rack) window.sim.rack();
        else window.sim.reset([{x: window.sim.W*0.3, y: window.sim.H/2,
                                vx:0, vy:0, cue:true}]);
        window.sim.shoot && window.sim.shoot(0, 0);
        const st = window.sim.state();
        const c = st.find(b => b.cue) || st[0];
        const cv = document.querySelector('canvas');
        const r = cv.getBoundingClientRect();
        const sx = r.width / cv.width, sy = r.height / cv.height;
        return { vx: r.left + c.x * sx, vy: r.top + c.y * sy,
                 cx: c.x, cy: c.y, sx, sy };
    }""")


def test_playable_can_shoot(page):
    """GATE: a real mouse drag on the cue ball must launch it. If this fails the
    game is unplayable and meta caps the whole score at 0.5."""
    if not _has_api(page):
        pytest.skip("no api")
    page.evaluate("() => window.sim.resume && window.sim.resume()")
    info = _cue_viewport(page)
    # pull back down-right and release (pull-back sling)
    page.mouse.move(info["vx"], info["vy"])
    page.mouse.down()
    page.mouse.move(info["vx"] + 55 * info["sx"], info["vy"] + 40 * info["sy"], steps=6)
    page.mouse.up()
    page.evaluate("() => window.sim.pause && window.sim.pause()")
    moved = page.evaluate("""() => {
        const before = (window.sim.state().find(b=>b.cue)||window.sim.state()[0]);
        for (let i=0;i<40;i++) window.sim.step(1/240);
        const after = (window.sim.state().find(b=>b.cue)||window.sim.state()[0]);
        return Math.hypot(after.x-before.x, after.y-before.y);
    }""")
    assert moved > 6, "dragging the cue ball did not shoot it — not playable"


def test_has_reset_control(page):
    if not _has_api(page):
        pytest.skip("no api")
    # a visible reset/rack control that returns the balls to a start
    clicked = page.evaluate("""() => {
        const btns = [...document.querySelectorAll('button,[role=button],a,input[type=button]')];
        const b = btns.find(e => /reset|rack|new game|break|re-?rack/i.test(e.textContent||e.value||''));
        if (!b) return false;
        // move a ball, click reset, see the layout restored
        window.sim.reset([{x:400,y:200,vx:0,vy:0,cue:true}]);
        const n0 = window.sim.state().length;
        b.click();
        return window.sim.state().length > n0;  // rack restored more balls
    }""")
    assert clicked, "no working reset/rack control found"


def test_shows_instructions(page):
    if not _has_api(page):
        pytest.skip("no api")
    txt = page.evaluate("() => (document.body.innerText || '').toLowerCase()")
    # must name the actual mechanic (drag), not just say "shoot" vaguely — the
    # point is telling the player HOW, so an odd control still gets documented
    assert "drag" in txt, "on-screen instructions must tell the player to drag"
