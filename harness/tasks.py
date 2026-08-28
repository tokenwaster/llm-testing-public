
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import config
from .util import hash_dir


@dataclass
class Task:
    id: str
    category: str
    tier: int
    title: str
    path: Path
    prompt: str
    scoring: dict = field(default_factory=dict)
    timeout_s: int = config.DEFAULT_REQUEST_TIMEOUT_S
    max_retries: int = config.DEFAULT_MAX_RETRIES
    max_turns: int = config.DEFAULT_AGENT_MAX_TURNS
    checker_timeout_s: int = config.CHECKER_TIMEOUT_S
    content_hash: str = ""
    staging: bool = False

    @property
    def scoring_type(self) -> str:
        return self.scoring.get("type", "manual")

    @property
    def checker(self) -> Path | None:
        p = self.path / "checker.py"
        return p if p.exists() else None

    @property
    def setup_dir(self) -> Path | None:
        p = self.path / "setup"
        return p if p.is_dir() else None


def _load_task(task_dir: Path, category: str) -> Task:
    meta = yaml.safe_load((task_dir / "meta.yaml").read_text(encoding="utf-8")) or {}
    prompt = (task_dir / "prompt.md").read_text(encoding="utf-8")
    agentic = meta.get("agentic") or {}
    return Task(
        id=str(meta.get("id", task_dir.name)),
        category=str(meta.get("category", category)),
        tier=int(meta.get("tier", 1)),
        title=str(meta.get("title", task_dir.name)),
        path=task_dir,
        prompt=prompt,
        scoring=meta.get("scoring") or {},
        timeout_s=int(meta.get("timeout_s", config.DEFAULT_REQUEST_TIMEOUT_S)),
        max_retries=int(meta.get("max_retries", config.DEFAULT_MAX_RETRIES)),
        max_turns=int(agentic.get("max_turns", config.DEFAULT_AGENT_MAX_TURNS)),
        checker_timeout_s=int(meta.get("checker_timeout_s", config.CHECKER_TIMEOUT_S)),
        content_hash=hash_dir(task_dir)[:16],
    )


def _scan(tasks_dir: Path, staging: bool) -> list[Task]:
    tasks: list[Task] = []
    if not tasks_dir.is_dir():
        return tasks
    for category_dir in sorted(p for p in tasks_dir.iterdir() if p.is_dir()):
        for task_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
            if (task_dir / "meta.yaml").exists() and (task_dir / "prompt.md").exists():
                t = _load_task(task_dir, category_dir.name)
                t.staging = staging
                tasks.append(t)
    return tasks


def load_tasks(tasks_dir: Path | None = None,
               include_staging: bool = False) -> list[Task]:
    """The live suite is tasks/. tasks-staging/ holds candidates awaiting a
    calibration run: runnable when named explicitly, never part of the
    default set — so reports, coverage and the lens do not count them."""
    tasks = _scan(tasks_dir or config.TASKS_DIR, staging=False)
    if include_staging and tasks_dir is None:
        tasks += _scan(config.STAGING_DIR, staging=True)
    ids = [t.id for t in tasks]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Duplicate task ids: {sorted(dupes)}")
    return tasks
