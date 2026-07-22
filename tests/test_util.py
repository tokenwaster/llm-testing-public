"""robust_rmtree: tolerate Windows file locks / read-only files during delete.

The /run delete-run and delete-result endpoints used a bare shutil.rmtree,
which on Windows crashed the request-handler thread (WinError 32 lock /
WinError 5 read-only) and dumped a traceback to the console. robust_rmtree
clears read-only bits, retries transient locks with backoff, and reports
failure as a bool so the endpoint returns a clean 409 instead of crashing.
"""
import os
import stat

from harness import util
from harness.util import robust_rmtree


def test_removes_normal_tree(tmp_path):
    d = tmp_path / "run"
    (d / "model" / "task" / "workspace").mkdir(parents=True)
    (d / "model" / "task" / "workspace" / "a.py").write_text("x")
    assert robust_rmtree(d) is True
    assert not d.exists()


def test_removes_read_only_file(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    f = d / "ro.txt"
    f.write_text("x")
    os.chmod(f, stat.S_IREAD)
    assert robust_rmtree(d) is True
    assert not d.exists()


def test_missing_path_is_success(tmp_path):
    assert robust_rmtree(tmp_path / "does-not-exist") is True


def test_persistent_lock_returns_false_without_raising(tmp_path, monkeypatch):
    import shutil
    d = tmp_path / "locked"
    d.mkdir()
    def _always_locked(*a, **k):
        raise PermissionError(32, "in use by another process")
    monkeypatch.setattr(shutil, "rmtree", _always_locked)
    monkeypatch.setattr(util.time, "sleep", lambda *_: None)
    assert robust_rmtree(d, tries=3) is False
    assert d.exists()



def test_rescore_refuses_while_a_run_is_executing(tmp_path, monkeypatch):
    import pytest
    from harness import config, rescore
    runs = tmp_path / "runs"
    (runs / "2026-01-01_000000").mkdir(parents=True)
    util_write = __import__("harness.util", fromlist=["write_json"]).write_json
    util_write(runs / "2026-01-01_000000" / "run.json",
               {"run_id": "2026-01-01_000000", "finished": None})
    monkeypatch.setattr(config, "RUNS_DIR", runs)
    assert rescore._active_run() == "2026-01-01_000000"
    with pytest.raises(rescore.RunInProgress):
        rescore._rescore("*", progress=lambda *_: None)


def test_rescore_proceeds_when_all_runs_finished(tmp_path, monkeypatch):
    from harness import config, rescore
    runs = tmp_path / "runs"
    (runs / "2026-01-01_000000").mkdir(parents=True)
    util_write = __import__("harness.util", fromlist=["write_json"]).write_json
    util_write(runs / "2026-01-01_000000" / "run.json",
               {"run_id": "2026-01-01_000000", "finished": "2026-01-01T01:00:00Z"})
    monkeypatch.setattr(config, "RUNS_DIR", runs)
    assert rescore._active_run() is None


def test_hash_dir_ignores_bytecode(tmp_path):
    """Bytecode is not content. rglob("*") swept __pycache__ in, so running a
    task's checker changed the task's identity - 33 of v0.5's 39 tasks logged
    two or three hashes for content that never moved."""
    from harness.util import hash_dir
    (tmp_path / "checker.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "meta.yaml").write_text("id: t\n", encoding="utf-8")
    before = hash_dir(tmp_path)
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "checker.cpython-314.pyc").write_bytes(b"\x00compiled junk")
    assert hash_dir(tmp_path) == before, \
        "compiling a checker must not change the task's content hash"
    (tmp_path / "prompt.md").write_text("hello\n", encoding="utf-8")
    assert hash_dir(tmp_path) != before, "a REAL content change must still show"
