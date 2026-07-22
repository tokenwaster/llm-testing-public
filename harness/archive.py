"""Versioned dataset archiving.

Test suites are versioned major.minor.patch (SUITE_VERSION). When tests or
methodology change (minor/major bump), the old runs are archived under their
major.minor key so live reports only ever show one coherent dataset:

    harness archive --as 0.2      move ALL live runs + a tasks/ snapshot
                                  into archive/v0.2/
    harness archive --list        enumerate archived datasets
    harness report --dataset 0.2  render a full static report site for an
                                  archived set -> reports/datasets/v0.2/
"""

import re
import shutil

from . import config
from .util import now_iso, read_json, write_json


def norm_key(version: str) -> str:
    """'v0.2', '0.2', '0.2.1' -> '0.2' (major.minor is the dataset key)."""
    m = re.match(r"v?(\d+)\.(\d+)", version.strip())
    if not m:
        raise ValueError(f"bad version key: {version!r} (want major.minor)")
    return f"{m.group(1)}.{m.group(2)}"


def archive_current(version: str, progress=print) -> int:
    """Move every live run into archive/v<major.minor>/runs/ and snapshot the
    task definitions alongside them (once per key)."""
    key = norm_key(version)
    dest = config.ARCHIVE_DIR / f"v{key}"
    dest_runs = dest / "runs"
    dest_runs.mkdir(parents=True, exist_ok=True)

    moved = 0
    if config.RUNS_DIR.exists():
        for d in sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir()):
            target = dest_runs / d.name
            if target.exists():
                progress(f"  ! {d.name} already in archive v{key} — skipped")
                continue
            shutil.move(str(d), str(target))
            moved += 1
            progress(f"  archived {d.name}")

    snap = dest / "tasks"
    if not snap.exists() and config.TASKS_DIR.exists():
        shutil.copytree(config.TASKS_DIR, snap)
        progress(f"  task definitions snapshotted to archive/v{key}/tasks")

    manifest = read_json(dest / "dataset.json", {"key": key, "archived": []})
    manifest["archived"].append({"at": now_iso(), "runs_moved": moved})
    write_json(dest / "dataset.json", manifest)
    progress(f"v{key}: {moved} run(s) archived")
    return moved


def list_archives() -> list[dict]:
    out = []
    if not config.ARCHIVE_DIR.exists():
        return out
    for d in sorted(config.ARCHIVE_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("v"):
            n = len([p for p in (d / "runs").iterdir() if p.is_dir()]) \
                if (d / "runs").is_dir() else 0
            out.append({"key": d.name[1:], "runs": n,
                        "has_tasks_snapshot": (d / "tasks").is_dir()})
    return out


def render_dataset(version: str, progress=print, out_dir=None,
                   public_nav: bool = False):
    """Render a complete static report site for an archived dataset. `out_dir`
    overrides the destination (default reports/datasets/vKEY); `public_nav=True`
    drops the operator-only control links (for the public export)."""
    from . import report
    key = norm_key(version)
    src = config.ARCHIVE_DIR / f"v{key}" / "runs"
    if not src.is_dir():
        raise FileNotFoundError(f"no archived dataset v{key} "
                                f"(expected {src})")
    out = out_dir or (config.REPORTS_DIR / "datasets" / f"v{key}")
    snap = src.parent / "tasks"
    index = report.generate_all(runs_dir=src, out_dir=out,
                                dataset_label=f"archived dataset v{key}",
                                dataset_key=key,
                                tasks_dir=snap if snap.is_dir() else None,
                                public_nav=public_nav)
    progress(f"dataset v{key} rendered: {index}")
    return index
