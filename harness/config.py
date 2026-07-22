"""Paths and constants. Everything is relative to the project root."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT / "archive"

SETTINGS_FILE = ROOT / "settings.local.json"
DEFAULT_SERVE_PORT = 8765


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_setting(key: str, value) -> None:
    """Persist one preference to settings.local.json (merges with existing)."""
    s = load_settings()
    s[key] = value
    SETTINGS_FILE.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def serve_port() -> int:
    """The saved default serve port, else the built-in 8765."""
    p = load_settings().get("serve_port")
    try:
        return int(p) if p else DEFAULT_SERVE_PORT
    except (TypeError, ValueError):
        return DEFAULT_SERVE_PORT


def suite_version() -> str:
    """Current test-suite version (major.minor.patch) from SUITE_VERSION.
    Minor/major bumps mean tests or methodology changed — archive the old
    runs first. Patch bumps are non-methodology fixes."""
    try:
        return (ROOT / "SUITE_VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def _load_dotenv() -> None:
    """Minimal .env loader (KEY=VALUE) so keys travel with the project. Real
    environment variables win over .env values."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()
MODELS_DIR = ROOT / "models"
TASKS_DIR = ROOT / "tasks"
RUNS_DIR = ROOT / "runs"
SCOUTS_DIR = ROOT / "scouts"
REPORTS_DIR = ROOT / "reports"

DEFAULT_REQUEST_TIMEOUT_S = 180
DEFAULT_MAX_RETRIES = 2
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.2
DEFAULT_AGENT_MAX_TURNS = 15
CLAUDE_SPIRAL_S = 300

CHECKER_TIMEOUT_S = 60
TOOL_RUN_TIMEOUT_S = 60
TOOL_OUTPUT_LIMIT = 6000

HARDENED_TASKS = (
    "web-012-coin",
    "rs-010-ants-rod",
    "ctx-012-aggregate-reversals-32k",
    "web-003-sand",
    "web-002-maze",
    "ag-006-perf-optimize",
    "ag-007-regression-hunt",
    "rs-006-string-pipeline",
    "py-005-csv-parser",
)

NEW_TASKS = (
    "if-001-format-exact",
    "if-002-constraint-stack",
    "hl-001-grounded-qa",
    "hl-002-abstain-hard",
    "math-001-multistep",
    "math-002-rate-mix",
    "ext-001-fields-json",
    "ext-002-nested-normalize",
    "tool-001-select-call",
    "tool-002-select-hard",
)

def hardened_completion(counts: dict[str, int], hard_ids) -> dict:
    """How many times the hardened set has been fully swept for one model.

    `counts` maps hardened-task id -> number of scored runs of that task. A full
    run and a hardened-only set each score every hardened task once, so the
    number of COMPLETE sweeps is the minimum count across the hardened tasks;
    any task with more than that minimum means an extra sweep is partway done.

    `hard_todo` is the tasks lagging at that minimum WHEN a sweep is partway done
    — running exactly those once lifts the minimum and completes the next sweep.
    It is empty when nothing is in progress (all equal), so there's nothing to
    click to 'finish'."""
    hard_ids = list(hard_ids)
    per = [counts.get(t, 0) for t in hard_ids]
    done = min(per) if per else 0
    partial = any(c > done for c in per)
    return {"hard_done": done,
            "hard_partial": partial,
            "hard_total": len(hard_ids),
            "hard_todo": [t for t in hard_ids
                          if counts.get(t, 0) == done] if partial else []}


ANSWER_INSTRUCTION = (
    "\n\nWhen you are finished, output your final answer on its own line, "
    "as the last line of your response, in the exact format:\nANSWER: <your answer>"
)

CODE_INSTRUCTION = (
    "\n\nRespond with a single fenced Python code block containing the complete "
    "contents of solution.py. Do not include any code outside the block."
)

HTML_INSTRUCTION = (
    "\n\nRespond with a single fenced ```html code block containing the complete "
    "contents of app.html — one fully self-contained file with all CSS and "
    "JavaScript inline. No external resources (no CDNs, fonts, or images). "
    "Do not include anything outside the code block."
)
