"""A checker deadline must reap the whole tree, not just the direct child.

Checkers spawn (pytest, ag-006's timed workloads, Playwright's node+Chromium),
and a venv python.exe is a launcher shim, so killing one process leaves the real
interpreter running. Orphans steal the CPU that ag-006 and the webapp lane
calibrate their budgets against, corrupting the scores of tasks that run later.
"""

import os
import subprocess
import sys
import time

import pytest

from harness.util import run_capped, terminate_tree

pytestmark = pytest.mark.skipif(
    not hasattr(subprocess, "Popen"), reason="needs real processes")

MARKER = "tree_kill_probe_marker"
PARENT = f"""
import subprocess, sys, time
sys.stdout.write("SPAWNED\\n"); sys.stdout.flush()
subprocess.Popen([sys.executable, "-c", "# {MARKER}\\nwhile True: pass"])
while True:
    time.sleep(0.05)
"""


def _spinners_alive() -> int:
    """Count live probe grandchildren, by command line."""
    if os.name == "nt":
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             f"Where-Object {{ $_.CommandLine -like '*{MARKER}*' }}).Count"],
            capture_output=True, text=True)
        return int((r.stdout or "0").strip() or 0)
    r = subprocess.run(["pgrep", "-fc", MARKER], capture_output=True, text=True)
    return int((r.stdout or "0").strip() or 0)


def _reap_strays():
    if os.name == "nt":
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             f"Where-Object {{ $_.CommandLine -like '*{MARKER}*' }} | "
             "ForEach-Object { taskkill /F /T /PID $_.ProcessId }"],
            capture_output=True)
    else:
        subprocess.run(["pkill", "-9", "-f", MARKER], capture_output=True)


@pytest.fixture(autouse=True)
def no_strays():
    _reap_strays()
    yield
    _reap_strays()


def test_run_capped_kills_the_grandchild_too():
    before = _spinners_alive()
    res = run_capped([sys.executable, "-c", PARENT], timeout=3)
    assert res.timed_out, "the parent never exits; it must hit the deadline"
    assert res.returncode is None, "a killed process reports no returncode"
    time.sleep(1.5)
    assert _spinners_alive() == before, (
        "a grandchild outlived the deadline — this is the fan that won't stop, "
        "and it steals CPU from every timing-scored task that runs after it")


def test_run_capped_leaves_a_normal_process_alone():
    res = run_capped([sys.executable, "-c", "print('done')"], timeout=30)
    assert res.timed_out is False
    assert res.returncode == 0
    assert "done" in res.stdout


def test_run_capped_reports_a_crash_rather_than_a_timeout():
    """A non-zero exit must not be mistaken for a deadline kill."""
    res = run_capped([sys.executable, "-c", "raise SystemExit(3)"], timeout=30)
    assert res.timed_out is False
    assert res.returncode == 3


def test_terminate_tree_is_safe_on_an_already_dead_process():
    proc = subprocess.Popen([sys.executable, "-c", "pass"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate(timeout=30)
    terminate_tree(proc)


def test_the_scoring_lane_uses_the_capped_runner():
    """The checker deadline is the one that fires on real leaks — every pytest
    and webapp task in the suite goes through it."""
    import inspect

    from harness import scoring
    src = inspect.getsource(scoring.run_pytest_checker)
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#"))
    assert "run_capped" in code
    assert "subprocess.run(" not in code, (
        "subprocess.run(timeout=) here orphans the checker's whole subtree")
