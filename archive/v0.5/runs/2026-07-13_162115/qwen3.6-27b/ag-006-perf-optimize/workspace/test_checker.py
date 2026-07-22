"""Correctness + timing checker. Each function is graded by ONE test that
requires BOTH correctness (edge cases in-process) AND speed (production-sized
input in a killable subprocess). Leaving a function slow, or breaking it while
optimizing, fails that function's test — an untouched (correct-but-slow) seed
scores 0, not half credit.

Every timed workload runs in its own SUBPROCESS with a hard kill, so a slow
(or hung) implementation fails its one test instead of hanging the suite."""
import subprocess
import sys
from pathlib import Path

# The budget must measure the ALGORITHM, not the CPU.
#
# The original 2.0s absolute budget did the latter: a correct O(n) solution runs
# in ~0.3s idle, so it had only a ~6x margin, and on a loaded machine a genuinely
# optimized submission blew the budget and scored ZERO. (Observed: claude-haiku's
# saved workspace passes 4/4 in 0.30s on an idle box, yet scored 0.0 during a
# busy run. Same code, same checker — only the machine load differed.) That is a
# benchmark measuring how busy the computer was.
#
# The gap we actually want to detect is algorithmic and enormous: O(n) is ~0.3s
# while the naive O(n^2)/exponential seed takes MINUTES. So we do two things:
#   1. widen the base budget (huge margin, still nowhere near the naive seed), and
#   2. CALIBRATE it to the machine — time a fixed reference workload in the same
#      subprocess and scale the budget by how slow this box is right now. Under
#      load both the calibration and the workload slow down together, so the
#      verdict is load-invariant.
BUDGET_S = 8.0            # base budget on a reference-speed machine
CALIB_BASELINE_S = 0.20   # how long CALIB_SNIPPET takes on an idle reference box
MAX_FACTOR = 4.0          # cap: don't let a pathological box grant an infinite budget
KILL_S = 45.0             # hard subprocess kill: slow = failed, never hung

# A fixed, pure-CPU workload. Its runtime is the machine's current speed.
CALIB_SNIPPET = (
    "tc0 = time.perf_counter()\n"
    "_acc = 0\n"
    "for _i in range(2000000):\n"
    "    _acc += _i * _i\n"
    "calib = time.perf_counter() - tc0\n")

WS = Path(__file__).parent


def _budgeted(snippet: str) -> tuple[bool, str]:
    """Run `snippet` (which must print a result) in a subprocess from the
    workspace. Returns (within_calibrated_budget_and_ok, stdout_or_reason)."""
    code = (
        "import sys, time\n"
        f"sys.path.insert(0, {str(WS)!r})\n"
        "import perf\n"
        + CALIB_SNIPPET +
        "t0 = time.perf_counter()\n"
        + snippet + "\n"
        "dt = time.perf_counter() - t0\n"
        "print(f'CALIB {calib:.4f}')\n"
        "print(f'ELAPSED {dt:.3f}')\n")
    try:
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True, timeout=KILL_S)
    except subprocess.TimeoutExpired:
        return False, (f"killed after {KILL_S}s — far beyond any calibrated "
                       f"budget (base {BUDGET_S}s)")
    if proc.returncode != 0:
        return False, (proc.stderr or "crashed")[-300:]
    out = proc.stdout.strip().splitlines()
    elapsed = float(out[-1].split()[1])
    calib = float(out[-2].split()[1])
    # how much slower is this machine, right now, than the reference box?
    factor = min(max(calib / CALIB_BASELINE_S, 1.0), MAX_FACTOR)
    budget = BUDGET_S * factor
    if elapsed > budget:
        return False, (f"took {elapsed:.2f}s (budget {budget:.1f}s = "
                       f"{BUDGET_S}s x{factor:.1f} machine factor)")
    return True, "\n".join(out[:-2])


# correctness edge cases run in-process (cheap on any implementation); the
# timed workloads below ALSO assert correctness on large inputs.
sys.path.insert(0, str(WS))
from perf import common_elements, count_pairs, dedupe_keep_order, fib  # noqa: E402


# ---- one test per function: must be BOTH correct AND fast to pass ----------

def test_common_elements():
    # correctness incl. edge cases
    assert common_elements([3, 1, 2, 3], [2, 3, 9]) == [2, 3]
    assert common_elements([], [1]) == []
    assert common_elements([5, 5], [5]) == [5]
    # speed on production-sized input (also re-checks correctness)
    ok, info = _budgeted(
        "import random\n"
        "rng = random.Random(7)\n"
        "a = [rng.randrange(500000) for _ in range(200000)]\n"
        "b = [rng.randrange(500000) for _ in range(200000)]\n"
        "t0 = time.perf_counter()\n"
        "out = perf.common_elements(a, b)\n"
        "assert out == sorted(set(a) & set(b)), 'wrong result'")
    assert ok, f"common_elements @200k: {info}"


def test_fib():
    # correctness incl. edge cases
    assert fib(0) == 0 and fib(1) == 1
    assert fib(10) == 55
    assert fib(20) == 6765
    # speed: fib(300) is unreachable by exponential recursion
    a, b = 0, 1
    for _ in range(300):
        a, b = b, a + b
    ok, info = _budgeted(
        "t0 = time.perf_counter()\n"
        f"assert perf.fib(300) == {a}, 'wrong fib(300)'")
    assert ok, f"fib(300): {info}"


def test_count_pairs():
    # correctness incl. edge cases
    assert count_pairs([1, 2, 3, 4], 5) == 2
    assert count_pairs([2, 2, 2], 4) == 3
    assert count_pairs([], 1) == 0
    # speed on production-sized input (also re-checks correctness)
    ok, info = _budgeted(
        "import random\n"
        "from collections import Counter\n"
        "rng = random.Random(11)\n"
        "nums = [rng.randrange(1000) for _ in range(100000)]\n"
        "c = Counter(nums)\n"
        "expect = 0\n"
        "for v, n in c.items():\n"
        "    w = 1000 - v\n"
        "    if w == v: expect += n * (n - 1) // 2\n"
        "    elif w in c and w > v: expect += n * c[w]\n"
        "t0 = time.perf_counter()\n"
        "assert perf.count_pairs(nums, 1000) == expect, 'wrong count'")
    assert ok, f"count_pairs @100k: {info}"


def test_dedupe():
    # correctness incl. edge cases
    assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe_keep_order([]) == []
    # speed on production-sized input (also re-checks correctness)
    ok, info = _budgeted(
        "import random\n"
        "rng = random.Random(13)\n"
        "items = [rng.randrange(50000) for _ in range(200000)]\n"
        "seen = set(); expect = []\n"
        "for x in items:\n"
        "    if x not in seen: seen.add(x); expect.append(x)\n"
        "t0 = time.perf_counter()\n"
        "assert perf.dedupe_keep_order(items) == expect, 'wrong result'")
    assert ok, f"dedupe @200k: {info}"
